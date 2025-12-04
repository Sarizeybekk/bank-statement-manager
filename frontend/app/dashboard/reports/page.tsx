"use client";

import { useEffect, useState } from "react";
import { reportsAPI } from "@/lib/api";
import { format, subDays } from "date-fns";
import { BarChart3, TrendingUp, TrendingDown, DollarSign } from "lucide-react";
import SummaryCard from "@/components/SummaryCard";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function ReportsPage() {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start_date: (() => {
      const date = new Date();
      date.setMonth(date.getMonth() - 12);
      date.setDate(1);
      return format(date, "yyyy-MM-dd");
    })(),
    end_date: format(new Date(), "yyyy-MM-dd"),
  });
  const [targetCurrency, setTargetCurrency] = useState("");

  useEffect(() => {
    loadReport();
  }, [dateRange, targetCurrency]);

  const loadReport = async () => {
    setLoading(true);
    try {
      const data = await reportsAPI.summary({
        ...dateRange,
            target_currency: targetCurrency || undefined,
          });
          setSummary(data);
        } catch (error) {
        } finally {
      setLoading(false);
    }
  };

  const chartData = summary?.top_expense_categories?.map((cat: any) => ({
    name: cat.category,
    amount: cat.amount,
    count: cat.count,
  })) || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Finansal Raporlar</h1>
          <p className="text-gray-600 mt-1">Finansal verilerinizi analiz edin</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Başlangıç Tarihi</label>
            <input
              type="date"
              value={dateRange.start_date}
              onChange={(e) => setDateRange({ ...dateRange, start_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Bitiş Tarihi</label>
            <input
              type="date"
              value={dateRange.end_date}
              onChange={(e) => setDateRange({ ...dateRange, end_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Para Birimi</label>
            <select
              value={targetCurrency}
              onChange={(e) => setTargetCurrency(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Tüm Para Birimleri</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="TRY">TRY</option>
              <option value="GBP">GBP</option>
            </select>
          </div>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SummaryCard
            title="Toplam Gelir"
            value={summary.total_income}
            currency={summary.currency || "MIXED"}
            icon={<TrendingUp className="w-6 h-6" />}
            color="success"
          />
          <SummaryCard
            title="Toplam Gider"
            value={summary.total_expense}
            currency={summary.currency || "MIXED"}
            icon={<TrendingDown className="w-6 h-6" />}
            color="danger"
          />
          <SummaryCard
            title="Net Nakit Akışı"
            value={summary.net_cash_flow}
            currency={summary.currency || "MIXED"}
            icon={<DollarSign className="w-6 h-6" />}
            color={summary.net_cash_flow >= 0 ? "success" : "danger"}
          />
        </div>
      )}

      {summary && chartData.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center gap-2 mb-6">
            <BarChart3 className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">En Çok Harcama Yapılan Kategoriler</h2>
          </div>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="amount" fill="#22c55e" name="Tutar" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {summary && summary.top_expense_categories && summary.top_expense_categories.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Gider Dağılımı</h2>
          <div className="space-y-3">
            {summary.top_expense_categories.map((cat: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{cat.category || "Kategorisiz"}</p>
                  <p className="text-sm text-gray-500">{cat.count} işlem</p>
                </div>
                <p className="text-lg font-semibold text-danger-600">
                  {cat.amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}{" "}
                  {summary.currency || "MIXED"}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      )}
    </div>
  );
}

