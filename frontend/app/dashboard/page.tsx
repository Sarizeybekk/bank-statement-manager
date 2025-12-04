"use client";

import { useEffect, useState } from "react";
import { transactionsAPI, reportsAPI } from "@/lib/api";
import { format } from "date-fns";
import { Upload, TrendingUp, TrendingDown, DollarSign, FileText } from "lucide-react";
import TransactionList from "@/components/TransactionList";
import SummaryCard from "@/components/SummaryCard";
import UploadModal from "@/components/UploadModal";

export default function DashboardPage() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [selectedCurrency, setSelectedCurrency] = useState("");

  const [endDate] = useState(() => {
    const date = new Date();
    // Set to end of current month
    date.setDate(1);
    date.setMonth(date.getMonth() + 1);
    date.setDate(0);
    return date;
  });
  const [startDate] = useState(() => {
    const date = new Date();
    // Show last 12 months by default to catch all transactions
    date.setMonth(date.getMonth() - 12);
    date.setDate(1); // Start of month
    return date;
  });

  useEffect(() => {
    loadData();
  }, [selectedCurrency]);

  const loadData = async () => {
    setLoading(true);
    try {
      const startDateStr = format(startDate, "yyyy-MM-dd");
      const endDateStr = format(endDate, "yyyy-MM-dd");
      
      const [transactionsData, summaryData] = await Promise.all([
        transactionsAPI.list({
          start_date: startDateStr,
          end_date: endDateStr,
          target_currency: selectedCurrency || undefined,
        }),
        reportsAPI.summary({
          start_date: startDateStr,
          end_date: endDateStr,
          target_currency: selectedCurrency || undefined,
        }),
      ]);

      setTransactions(transactionsData.results || transactionsData || []);
      setSummary(summaryData);
    } catch (error: any) {
      setTransactions([]);
      setSummary(null);
    } finally {
      setLoading(false);
    }
  };

    const handleUploadSuccess = () => {
    setShowUpload(false);
    setTimeout(() => {
      loadData();
    }, 1000);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Kontrol Paneli</h1>
          <p className="text-gray-600 mt-1">Finansal işlemlerinizin genel bakışı</p>
        </div>
        <div className="flex gap-3">
          <select
            value={selectedCurrency}
            onChange={(e) => setSelectedCurrency(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">Tüm Para Birimleri</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="TRY">TRY</option>
            <option value="GBP">GBP</option>
          </select>
          <button
            onClick={() => setShowUpload(true)}
            className="flex items-center gap-2 bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors shadow-lg hover:shadow-xl"
          >
            <Upload className="w-5 h-5" />
            CSV Yükle
          </button>
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

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">Son İşlemler</h2>
          </div>
          {transactions.length > 0 && (
            <span className="text-sm text-gray-500">
              {transactions.length} işlem
            </span>
          )}
        </div>
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <>
            {transactions.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 mb-2">İşlem bulunamadı</p>
                <p className="text-sm text-gray-400">
                  Başlamak için bir CSV dosyası yükleyin
                </p>
              </div>
            ) : (
              <TransactionList transactions={transactions} />
            )}
          </>
        )}
      </div>

      {showUpload && <UploadModal onClose={() => setShowUpload(false)} onSuccess={handleUploadSuccess} />}
    </div>
  );
}

