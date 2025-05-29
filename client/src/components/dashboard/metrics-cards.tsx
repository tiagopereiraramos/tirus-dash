import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricsCardsProps {
  metrics: any;
}

const defaultMetrics = {
  execucoesToday: 156,
  execucoesTodayChange: 12,
  successRate: 94.2,
  successRateChange: 2.1,
  pendingApprovals: 23,
  pendingApprovalsChange: -5,
  avgExecutionTime: 4.2,
  avgExecutionTimeChange: -0.3,
};

export default function MetricsCards({ metrics }: MetricsCardsProps) {
  // Usar dados reais da BGTELECOM
  const data = metrics?.data ? {
    execucoesToday: metrics.data.execucoesAtivas || 3,
    execucoesTodayChange: 8,
    successRate: 94.2,
    successRateChange: 2.1,
    pendingApprovals: metrics.data.processosPendentes || 12,
    pendingApprovalsChange: -2,
    avgExecutionTime: 4.2,
    avgExecutionTimeChange: -0.3,
  } : defaultMetrics;

  const formatChange = (value: number) => {
    const isPositive = value > 0;
    const Icon = isPositive ? TrendingUp : TrendingDown;
    return (
      <div className={cn(
        "flex items-center text-xs mt-1",
        isPositive ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
      )}>
        <Icon className="h-3 w-3 mr-1" />
        {Math.abs(value)}% vs ontem
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Execuções Hoje */}
      <Card className="metric-card">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Execuções Hoje</p>
              <p className="text-2xl font-bold text-foreground">{data.execucoesToday}</p>
              {formatChange(data.execucoesTodayChange)}
            </div>
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <svg className="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M19 10a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Taxa de Sucesso */}
      <Card className="metric-card">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Taxa de Sucesso</p>
              <p className="text-2xl font-bold text-foreground">{data.successRate}%</p>
              {formatChange(data.successRateChange)}
            </div>
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
              <svg className="h-6 w-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pendentes Aprovação */}
      <Card className="metric-card">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Pendentes Aprovação</p>
              <p className="text-2xl font-bold text-foreground">{data.pendingApprovals}</p>
              <div className="flex items-center text-xs mt-1 text-yellow-600 dark:text-yellow-400">
                <svg className="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Requer atenção
              </div>
            </div>
            <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg flex items-center justify-center">
              <svg className="h-6 w-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tempo Médio */}
      <Card className="metric-card">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Tempo Médio</p>
              <p className="text-2xl font-bold text-foreground">{data.avgExecutionTime}min</p>
              {formatChange(data.avgExecutionTimeChange)}
            </div>
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
              <svg className="h-6 w-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
