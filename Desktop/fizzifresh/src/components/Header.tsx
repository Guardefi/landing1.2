import React from "react";
import { ScorpiusLogo } from "@/components/ScorpiusLogo";

type Props = {};

export default function Header({}: Props) {
  return (
    <header className="-mb-28 flex justify-center py-4">
      <ScorpiusLogo className="z-10 h-20 cursor-pointer text-cyan-400" />
    </header>
  );
}
