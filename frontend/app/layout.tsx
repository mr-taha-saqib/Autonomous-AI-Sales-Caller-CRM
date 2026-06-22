import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Algorixe Sales Assistant",
  description: "AI-powered cold-calling & CRM platform for Algorixe Car Care.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
