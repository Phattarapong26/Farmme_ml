import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Database, Cpu, Zap, Activity, RefreshCw } from 'lucide-react';
import { useBackendHealth, useCacheStats, useTrainingStatus } from '@/hooks/useBackendAPI';

const BackendStatus: React.FC = () => {
  const { data: health, isLoading: healthLoading } = useBackendHealth();
  const { data: cacheStats, isLoading: cacheLoading } = useCacheStats();
  const { data: trainingStatus, isLoading: trainingLoading } = useTrainingStatus();

  if (healthLoading || cacheLoading || trainingLoading) {
    return (
      <Card className="w-80">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            <span className="text-sm text-gray-500">กำลังโหลดสถานะระบบ...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* System Health */}
      <Card className="w-80">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-500" />
            สถานะระบบ
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm">ฐานข้อมูล</span>
            <Badge variant={health?.database_connected ? "default" : "destructive"}>
              {health?.database_connected ? "เชื่อมต่อแล้ว" : "ไม่เชื่อมต่อ"}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Redis Cache</span>
            <Badge variant={health?.redis_connected ? "default" : "destructive"}>
              {health?.redis_connected ? "เชื่อมต่อแล้ว" : "ไม่เชื่อมต่อ"}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">ML Model</span>
            <Badge variant={health?.model_loaded ? "default" : "secondary"}>
              {health?.model_loaded ? "โหลดแล้ว" : "ไม่โหลด"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Cache Statistics */}
      {cacheStats?.cache_stats && (
        <Card className="w-80">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-500" />
              สถิติ Cache
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">หน่วยความจำ</span>
              <span className="text-sm font-medium">{cacheStats.cache_stats.used_memory}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">การเชื่อมต่อ</span>
              <span className="text-sm font-medium">{cacheStats.cache_stats.connected_clients}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Cache Hit Rate</span>
              <span className="text-sm font-medium">
                {cacheStats.cache_stats.keyspace_hits > 0 
                  ? Math.round((cacheStats.cache_stats.keyspace_hits / (cacheStats.cache_stats.keyspace_hits + cacheStats.cache_stats.keyspace_misses)) * 100)
                  : 0}%
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Training Status */}
      {trainingStatus && (
        <Card className="w-80">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Cpu className="w-5 h-5 text-green-500" />
              สถานะการฝึกโมเดล
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">ข้อมูลการทำนาย</span>
              <span className="text-sm font-medium">{trainingStatus.data_counts?.price_predictions || 0} รายการ</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">โมเดลราคา</span>
              <Badge variant={trainingStatus.training_ready?.price ? "default" : "secondary"}>
                {trainingStatus.training_ready?.price ? "พร้อมฝึก" : "ไม่พร้อม"}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">โมเดลแนะนำ</span>
              <Badge variant={trainingStatus.training_ready?.recommendation ? "default" : "secondary"}>
                {trainingStatus.training_ready?.recommendation ? "พร้อมฝึก" : "ไม่พร้อม"}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* API Endpoints Info */}
      <Card className="w-80">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Database className="w-5 h-5 text-purple-500" />
            API Endpoints
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <p>• <code className="bg-gray-100 px-1 rounded">/predict</code> - การทำนายราคา</p>
            <p>• <code className="bg-gray-100 px-1 rounded">/recommend</code> - คำแนะนำพืช</p>
            <p>• <code className="bg-gray-100 px-1 rounded">/chat</code> - AI Chat</p>
            <p>• <code className="bg-gray-100 px-1 rounded">/models</code> - จัดการโมเดล</p>
            <p>• <code className="bg-gray-100 px-1 rounded">/training</code> - ฝึกโมเดล</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default BackendStatus;
