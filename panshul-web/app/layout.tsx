import type { Metadata } from "next";
import { Fraunces, Outfit } from "next/font/google";
import { AuthProvider } from "@/components/AuthProvider";
import { ChatProvider } from "@/components/ChatProvider";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { SideBot } from "@/components/SideBot";
import "./globals.css";

const display = Fraunces({ subsets: ["latin"], variable: "--font-display", display: "swap" });
const sans = Outfit({ subsets: ["latin"], variable: "--font-sans", display: "swap" });

export const metadata: Metadata = {
  title: "Panshul — Education OS",
  description: "A personal teacher, adaptive quizzes, career guidance, mock interviews, and startup mentorship.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable}`}>
      <body>
        <a className="skip" href="#content">Skip to content</a>
        <AuthProvider>
          <ChatProvider>
            <Header />
            <div className="app-body">
              <div className="main-col">
                <main id="content">{children}</main>
                <Footer />
              </div>
              <SideBot />
            </div>
          </ChatProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
