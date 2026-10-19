import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EstateIQ | Property Intelligence",
  description:
    "Machine-learning powered real estate valuation and comparable property analysis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}