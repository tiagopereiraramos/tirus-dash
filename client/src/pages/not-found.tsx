import { Link } from "wouter";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-4xl font-bold mb-4">404 - Página não encontrada</h1>
      <p className="text-gray-600 mb-8">A página que você está procurando não existe.</p>
      <Link href="/">
        <Button>Voltar ao Dashboard</Button>
      </Link>
    </div>
  );
}