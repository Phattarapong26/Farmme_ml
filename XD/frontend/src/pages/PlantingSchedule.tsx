import React from 'react';
import PlantingRecommendation from '@/components/PlantingRecommendation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Sprout, Calendar, TrendingUp, AlertCircle, Sparkles, Brain, Target, BarChart3, Zap, CheckCircle } from 'lucide-react';
import { GiBrain, GiArtificialIntelligence } from 'react-icons/gi';
import { MdAutoGraph, MdScience } from 'react-icons/md';
import { BsRobot, BsGraphUpArrow } from 'react-icons/bs';
import { IoSparkles } from 'react-icons/io5';

const PlantingSchedule = () => {
  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* Header with ML Badge */}
      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl shadow-lg">
                <Sprout className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  วางแผนการเพาะปลูกอัจฉริยะ
                </h1>
                <p className="text-muted-foreground mt-1">
                  วิเคราะห์ช่วงเวลาที่เหมาะสมด้วย AI & Machine Learning เพื่อผลกำไรสูงสุด
                </p>
              </div>
            </div>
          </div>
          <Badge variant="secondary" className="gap-2 px-4 py-2 text-sm">
            <GiArtificialIntelligence className="h-4 w-4" />
            AI-Powered Analytics
          </Badge>
        </div>

      </div>


      {/* Main Component */}
      <PlantingRecommendation />

    </div>
  );
};

export default PlantingSchedule;
