export interface LicenseInfo {
  id: string;
  type: string;
  status: string;
  holder: string;
  organization: string;
  issued_date: string;
  expiry_date: string;
  features: string[];
  max_users: number;
  current_users: number;
  api_limits?: Record<string, any>;
}

export interface WalletCheckRequest {
  address: string;
}

export interface TokenApproval {
  token_contract: string;
  spender: string;
  allowance: string;
  risk_level: string;
  last_updated: string;
}

export interface RevokeRequest {
  address: string;
  token_contract: string;
  spender: string;
}
