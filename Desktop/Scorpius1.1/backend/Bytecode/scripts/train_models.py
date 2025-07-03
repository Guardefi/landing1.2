#!/usr/bin/env python3
"""
Production-Ready Training Pipeline
Train the Siamese network and other models
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
import torch
import yaml
from models.siamese_network import SmartSDSiameseNetwork, SmartSDTrainer
from preprocessors.bytecode_normalizer import BytecodeNormalizer
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from utils.metrics import PerformanceMonitor, SimilarityMetrics

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BytecodeDataset(Dataset):
    """Dataset for bytecode similarity training"""

    def __init__(self, pairs: List[Tuple], labels: List[int], tokenizer):
        self.pairs = pairs
        self.labels = labels
        self.tokenizer = tokenizer
        self.normalizer = BytecodeNormalizer()

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        bytecode1, bytecode2 = self.pairs[idx]
        label = self.labels[idx]

        # Tokenize (simplified for now)
        tokens1 = self.tokenizer.encode(bytecode1)
        tokens2 = self.tokenizer.encode(bytecode2)

        return {
            "tokens1": torch.tensor(tokens1, dtype=torch.long),
            "tokens2": torch.tensor(tokens2, dtype=torch.long),
            "label": torch.tensor(label, dtype=torch.float),
        }


class BytecodeTokenizer:
    """Tokenizer for EVM bytecode"""

    def __init__(self, vocab_size: int = 10000):
        self.vocab_size = vocab_size
        self.token_to_id = {}
        self.id_to_token = {}
        self._build_vocab()

    def _build_vocab(self):
        """Build vocabulary from EVM opcodes"""
        # Add special tokens
        special_tokens = ["<PAD>", "<UNK>", "<START>", "<END>"]

        # EVM opcodes
        evm_opcodes = [
            "STOP",
            "ADD",
            "MUL",
            "SUB",
            "DIV",
            "SDIV",
            "MOD",
            "SMOD",
            "ADDMOD",
            "MULMOD",
            "EXP",
            "SIGNEXTEND",
            "LT",
            "GT",
            "SLT",
            "SGT",
            "EQ",
            "ISZERO",
            "AND",
            "OR",
            "XOR",
            "NOT",
            "BYTE",
            "SHL",
            "SHR",
            "SAR",
            "KECCAK256",
            "ADDRESS",
            "BALANCE",
            "ORIGIN",
            "CALLER",
            "CALLVALUE",
            "CALLDATALOAD",
            "CALLDATASIZE",
            "CALLDATACOPY",
            "CODESIZE",
            "CODECOPY",
            "GASPRICE",
            "EXTCODESIZE",
            "EXTCODECOPY",
            "RETURNDATASIZE",
            "RETURNDATACOPY",
            "EXTCODEHASH",
            "BLOCKHASH",
            "COINBASE",
            "TIMESTAMP",
            "NUMBER",
            "DIFFICULTY",
            "GASLIMIT",
            "POP",
            "MLOAD",
            "MSTORE",
            "MSTORE8",
            "SLOAD",
            "SSTORE",
            "JUMP",
            "JUMPI",
            "PC",
            "MSIZE",
            "GAS",
            "JUMPDEST",
            "CREATE",
            "CALL",
            "CALLCODE",
            "RETURN",
            "DELEGATECALL",
            "CREATE2",
            "STATICCALL",
            "REVERT",
            "INVALID",
            "SELFDESTRUCT",
        ]

        # Add PUSH, DUP, SWAP variants
        for i in range(1, 33):
            evm_opcodes.append(f"PUSH{i}")
        for i in range(1, 17):
            evm_opcodes.append(f"DUP{i}")
            evm_opcodes.append(f"SWAP{i}")

        # Build token mappings
        all_tokens = special_tokens + evm_opcodes
        for i, token in enumerate(all_tokens):
            self.token_to_id[token] = i
            self.id_to_token[i] = token

    def encode(self, bytecode: str) -> List[int]:
        """Encode bytecode to token IDs"""
        # Parse bytecode to opcodes (simplified)
        opcodes = self._parse_bytecode(bytecode)

        token_ids = [self.token_to_id.get("<START>", 2)]
        for opcode in opcodes:
            token_id = self.token_to_id.get(opcode, self.token_to_id.get("<UNK>", 1))
            token_ids.append(token_id)
        token_ids.append(self.token_to_id.get("<END>", 3))

        return token_ids

    def _parse_bytecode(self, bytecode: str) -> List[str]:
        """Parse bytecode to opcode list (simplified)"""
        if bytecode.startswith("0x"):
            bytecode = bytecode[2:]

        opcodes = []
        i = 0
        while i < len(bytecode):
            if i + 1 < len(bytecode):
                hex_byte = bytecode[i : i + 2]
                opcode = self._hex_to_opcode(hex_byte)
                if opcode:
                    opcodes.append(opcode)
                i += 2
            else:
                break
        return opcodes

    def _hex_to_opcode(self, hex_byte: str) -> str:
        """Convert hex byte to opcode (simplified)"""
        try:
            byte_val = int(hex_byte, 16)
            # Simplified mapping
            opcode_map = {
                0x00: "STOP",
                0x01: "ADD",
                0x02: "MUL",
                0x03: "SUB",
                0x50: "POP",
                0x51: "MLOAD",
                0x52: "MSTORE",
                0x54: "SLOAD",
                0x55: "SSTORE",
                0x56: "JUMP",
                0x57: "JUMPI",
                0x5B: "JUMPDEST",
                0xF3: "RETURN",
                0xFD: "REVERT",
            }

            if 0x60 <= byte_val <= 0x7F:
                return f"PUSH{byte_val - 0x5f}"
            elif 0x80 <= byte_val <= 0x8F:
                return f"DUP{byte_val - 0x7f}"
            elif 0x90 <= byte_val <= 0x9F:
                return f"SWAP{byte_val - 0x8f}"
            else:
                return opcode_map.get(byte_val, "UNKNOWN")
        except ValueError:
            return "UNKNOWN"


def collate_fn(batch):
    """Custom collate function for batching"""
    tokens1 = [item["tokens1"] for item in batch]
    tokens2 = [item["tokens2"] for item in batch]
    labels = torch.stack([item["label"] for item in batch])

    # Pad sequences
    tokens1_padded = torch.nn.utils.rnn.pad_sequence(tokens1, batch_first=True)
    tokens2_padded = torch.nn.utils.rnn.pad_sequence(tokens2, batch_first=True)

    # Calculate lengths
    lengths1 = [len(seq) for seq in tokens1]
    lengths2 = [len(seq) for seq in tokens2]

    return tokens1_padded, tokens2_padded, lengths1, lengths2, labels


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_training_data(data_path: str) -> dict:
    """Load and prepare training data"""
    if data_path.endswith(".json"):
        with open(data_path, "r") as f:
            data = json.load(f)
        return data
    elif data_path.endswith(".csv"):
        df = pd.read_csv(data_path)
        pairs = [(row["bytecode1"], row["bytecode2"]) for _, row in df.iterrows()]
        labels = df["label"].tolist()
        return {"pairs": pairs, "labels": labels}
    else:
        # Generate synthetic data for testing
        logger.warning("No data file found, generating synthetic data")
        return generate_synthetic_data()


def generate_synthetic_data(num_pairs: int = 1000) -> dict:
    """Generate synthetic training data for testing"""
    pairs = []
    labels = []

    base_bytecode = "6080604052348015600f57600080fd5b50"

    for i in range(num_pairs):
        # Create similar pairs
        if i % 2 == 0:
            bytecode1 = base_bytecode + hex(i)[2:].zfill(4)
            bytecode2 = base_bytecode + hex(i + 1)[2:].zfill(4)  # Similar
            label = 1
        else:
            bytecode1 = base_bytecode + hex(i)[2:].zfill(4)
            bytecode2 = "608060405234801561001057600080fd5b50" + hex(i * 10)[2:].zfill(
                4
            )  # Different
            label = 0

        pairs.append((bytecode1, bytecode2))
        labels.append(label)

    return {"pairs": pairs, "labels": labels}


def evaluate_model(model, dataloader, device):
    """Evaluate model on validation set"""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    y_true = []
    y_pred = []
    y_scores = []

    criterion = torch.nn.BCELoss()

    with torch.no_grad():
        for seq1, seq2, lengths1, lengths2, labels in dataloader:
            seq1, seq2 = seq1.to(device), seq2.to(device)
            labels = labels.to(device)

            similarity_scores, _, _, _ = model(seq1, seq2, lengths1, lengths2)

            loss = criterion(similarity_scores.squeeze(), labels)
            total_loss += loss.item()

            predicted = (similarity_scores.squeeze() > 0.5).float()
            correct += (predicted == labels).sum().item()
            total += labels.size(0)

            # Collect for detailed metrics
            y_true.extend(labels.cpu().numpy())
            y_pred.extend(predicted.cpu().numpy())
            y_scores.extend(similarity_scores.squeeze().cpu().numpy())

    # Calculate detailed metrics
    metrics = SimilarityMetrics.calculate_comprehensive_metrics(
        y_true, y_pred, y_scores
    )
    metrics["loss"] = total_loss / len(dataloader)

    return metrics


async def main():
    """Main training pipeline"""
    parser = argparse.ArgumentParser(description="Train bytecode similarity models")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/siamese_config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/training_data.json",
        help="Path to training data",
    )
    parser.add_argument(
        "--output", type=str, default="models/", help="Output directory for models"
    )
    parser.add_argument(
        "--device", type=str, default="auto", help="Device to use (auto, cpu, cuda)"
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        logger.info("Config file not found, using default configuration")
        config = {
            "vocab_size": 10000,
            "embedding_dim": 256,
            "hidden_dim": 512,
            "batch_size": 32,
            "epochs": 50,
            "learning_rate": 1e-4,
        }

    # Set device
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    logger.info(f"Training on device: {device}")
    logger.info(f"Configuration: {config}")

    # Load training data
    logger.info("Loading training data...")
    try:
        train_data = load_training_data(args.data)
    except FileNotFoundError:
        logger.info("Training data not found, generating synthetic data")
        train_data = generate_synthetic_data(2000)

    logger.info(f"Loaded {len(train_data['pairs'])} training pairs")

    # Split data
    train_pairs, val_pairs, train_labels, val_labels = train_test_split(
        train_data["pairs"],
        train_data["labels"],
        test_size=0.2,
        stratify=train_data["labels"],
        random_state=42,
    )

    # Create tokenizer
    tokenizer = BytecodeTokenizer(config["vocab_size"])

    # Create datasets
    train_dataset = BytecodeDataset(train_pairs, train_labels, tokenizer)
    val_dataset = BytecodeDataset(val_pairs, val_labels, tokenizer)

    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config["batch_size"],
        shuffle=True,
        collate_fn=collate_fn,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=config["batch_size"],
        shuffle=False,
        collate_fn=collate_fn,
    )

    # Initialize model
    model = SmartSDSiameseNetwork(
        vocab_size=config["vocab_size"],
        embedding_dim=config["embedding_dim"],
        hidden_dim=config["hidden_dim"],
    )

    # Initialize trainer
    trainer = SmartSDTrainer(model, device=device)

    # Performance monitoring
    monitor = PerformanceMonitor()

    # Training loop
    best_val_f1 = 0
    best_metrics = None

    logger.info(f"Starting training for {config['epochs']} epochs...")

    for epoch in range(config["epochs"]):
        logger.info(f"Epoch {epoch + 1}/{config['epochs']}")

        monitor.start_measurement()

        # Train
        train_metrics = trainer.train_epoch(train_loader)

        # Validate
        val_metrics = evaluate_model(model, val_loader, device)

        epoch_time = monitor.end_measurement(f"epoch_{epoch + 1}")

        logger.info(
            f"Train - Loss: {train_metrics['loss']:.4f}, "
            f"Accuracy: {train_metrics['accuracy']:.4f}"
        )
        logger.info(
            f"Val - Loss: {val_metrics['loss']:.4f}, "
            f"Accuracy: {val_metrics['accuracy']:.4f}, "
            f"F1: {val_metrics['f1_score']:.4f}, "
            f"Precision: {val_metrics['precision']:.4f}, "
            f"Recall: {val_metrics['recall']:.4f}"
        )
        logger.info(f"Epoch time: {epoch_time['duration']:.2f}s")

        # Save best model
        if val_metrics["f1_score"] > best_val_f1:
            best_val_f1 = val_metrics["f1_score"]
            best_metrics = val_metrics

            # Save model
            Path(args.output).mkdir(exist_ok=True)
            model_path = Path(args.output) / "best_siamese_model.pth"
            trainer.save_model(str(model_path))

            logger.info(f"New best model saved with F1: {best_val_f1:.4f}")

            # Save metrics
            metrics_path = Path(args.output) / "best_metrics.json"
            with open(metrics_path, "w") as f:
                json.dump(best_metrics, f, indent=2)

        # Early stopping
        if epoch > 10 and val_metrics["f1_score"] < best_val_f1 - 0.05:
            logger.info("Early stopping triggered")
            break

    # Final evaluation and visualization
    logger.info("Training completed!")
    logger.info(f"Best validation metrics: {best_metrics}")

    # Generate performance summary
    performance_summary = monitor.get_performance_summary()
    logger.info(f"Performance summary: {performance_summary}")

    # Save final results
    results = {
        "config": config,
        "best_metrics": best_metrics,
        "performance_summary": performance_summary,
        "total_epochs": epoch + 1,
    }

    results_path = Path(args.output) / "training_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Results saved to {results_path}")


if __name__ == "__main__":
    asyncio.run(main())
