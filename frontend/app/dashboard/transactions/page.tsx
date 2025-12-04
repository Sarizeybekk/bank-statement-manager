"use client";

import { useEffect, useState, useRef } from "react";
import { transactionsAPI } from "@/lib/api";
import { format } from "date-fns";
import TransactionList from "@/components/TransactionList";
import { Filter, Download, X } from "lucide-react";

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [categoryInput, setCategoryInput] = useState("");
  const categoryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [filters, setFilters] = useState({
    start_date: (() => {
      const date = new Date();
      date.setMonth(date.getMonth() - 12);
      date.setDate(1);
      return format(date, "yyyy-MM-dd");
    })(),
    end_date: format(new Date(), "yyyy-MM-dd"),
    type: "",
    currency: "",
    category: "",
    target_currency: "",
  });

  useEffect(() => {
    loadTransactions();
  }, [filters.start_date, filters.end_date, filters.type, filters.currency, filters.category, filters.target_currency]);

  useEffect(() => {
    if (categoryTimeoutRef.current) {
      clearTimeout(categoryTimeoutRef.current);
    }
    
    categoryTimeoutRef.current = setTimeout(() => {
      setFilters({ ...filters, category: categoryInput });
    }, 500);

    return () => {
      if (categoryTimeoutRef.current) {
        clearTimeout(categoryTimeoutRef.current);
      }
    };
  }, [categoryInput]);

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (filters.start_date) params.start_date = filters.start_date;
      if (filters.end_date) params.end_date = filters.end_date;
      if (filters.type) params.type = filters.type;
      if (filters.currency) params.currency = filters.currency;
      if (filters.category) params.category = filters.category;
      if (filters.target_currency) params.target_currency = filters.target_currency;
      
      const data = await transactionsAPI.list(params);
      setTransactions(data.results || []);
    } catch (error) {
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">İşlemler</h1>
          <p className="text-gray-600 mt-1">İşlemlerinizi görüntüleyin ve filtreleyin</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Filtreler</h2>
          </div>
          <button
            onClick={() => {
              setCategoryInput("");
              setFilters({
                start_date: (() => {
                  const date = new Date();
                  date.setMonth(date.getMonth() - 12);
                  date.setDate(1);
                  return format(date, "yyyy-MM-dd");
                })(),
                end_date: format(new Date(), "yyyy-MM-dd"),
                type: "",
                currency: "",
                category: "",
                target_currency: "",
              });
            }}
            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <X className="w-4 h-4" />
            Filtreleri Temizle
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Başlangıç Tarihi</label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Bitiş Tarihi</label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tür</label>
            <select
              value={filters.type}
              onChange={(e) => setFilters({ ...filters, type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Tümü</option>
              <option value="credit">Gelir</option>
              <option value="debit">Gider</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Para Birimi</label>
            <select
              value={filters.currency}
              onChange={(e) => setFilters({ ...filters, currency: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Tümü</option>
              <option value="TRY">TRY</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Kategori</label>
            <input
              type="text"
              value={categoryInput}
              onChange={(e) => setCategoryInput(e.target.value)}
              placeholder="Kategoriye göre filtrele (örn: Satış, Kira)"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Para Birimine Dönüştür</label>
            <select
              value={filters.target_currency}
              onChange={(e) => setFilters({ ...filters, target_currency: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Orijinal Para Birimi</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="TRY">TRY</option>
              <option value="GBP">GBP</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">İşlemler</h2>
          {!loading && (
            <span className="text-sm text-gray-500">
              {transactions.length} işlem bulundu
            </span>
          )}
        </div>
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <TransactionList transactions={transactions} />
        )}
      </div>
    </div>
  );
}

