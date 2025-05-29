import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { useState } from "react";

const mockData = [
  { name: "Seg", EMBRATEL: 45, VIVO: 32, DIGITALNET: 28, AZUTON: 15, OI: 8 },
  { name: "Ter", EMBRATEL: 52, VIVO: 38, DIGITALNET: 31, AZUTON: 18, OI: 12 },
  { name: "Qua", EMBRATEL: 48, VIVO: 42, DIGITALNET: 26, AZUTON: 22, OI: 10 },
  { name: "Qui", EMBRATEL: 61, VIVO: 35, DIGITALNET: 34, AZUTON: 19, OI: 14 },
  { name: "Sex", EMBRATEL: 55, VIVO: 41, DIGITALNET: 29, AZUTON: 21, OI: 11 },
  { name: "Sáb", EMBRATEL: 42, VIVO: 36, DIGITALNET: 33, AZUTON: 16, OI: 9 },
  { name: "Dom", EMBRATEL: 38, VIVO: 31, DIGITALNET: 27, AZUTON: 14, OI: 7 },
];

const colors = {
  EMBRATEL: "#3366FF",
  VIVO: "#8B5CF6", 
  DIGITALNET: "#00D68F",
  AZUTON: "#FFAA00",
  OI: "#EF4444",
};

export default function ExecutionChart() {
  const [period, setPeriod] = useState("7d");

  const { data: chartData } = useQuery({
    queryKey: ["/api/relatorios/execucoes", { period }],
    enabled: false, // Disabled to use mock data
  });

  const data = chartData || mockData;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Execuções por Operadora</CardTitle>
            <CardDescription>
              Acompanhe a performance de execução das operadoras ao longo do tempo
            </CardDescription>
          </div>
          <Select value={period} onValueChange={setPeriod}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Últimos 7 dias</SelectItem>
              <SelectItem value="30d">Últimos 30 dias</SelectItem>
              <SelectItem value="90d">Últimos 3 meses</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey="name" 
              className="text-muted-foreground"
              tick={{ fontSize: 12 }}
            />
            <YAxis 
              className="text-muted-foreground"
              tick={{ fontSize: 12 }}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                color: "hsl(var(--card-foreground))",
              }}
            />
            <Legend />
            {Object.entries(colors).map(([operadora, color]) => (
              <Line
                key={operadora}
                type="monotone"
                dataKey={operadora}
                stroke={color}
                strokeWidth={2}
                dot={{ fill: color, strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: color, strokeWidth: 2 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
