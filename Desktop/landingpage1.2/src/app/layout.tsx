import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'ScorpiusCore | Medieval High-Tech Alien War Room',
  description: 'Fortune 500-worthy cybersecurity platform with advanced 3D interface and real-time threat detection.',
  keywords: ['cybersecurity', 'threat detection', 'war room', 'enterprise security'],
  openGraph: {
    title: 'ScorpiusCore War Room',
    description: 'Advanced cybersecurity platform with immersive 3D interface',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className={`${inter.className} bg-war-room-void text-white antialiased`}>
        {children}
      </body>
    </html>
  );
} 