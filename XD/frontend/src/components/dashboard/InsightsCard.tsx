import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Lightbulb, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp,
  Leaf,
  DollarSign
} from 'lucide-react';

interface Insight {
  id: string;
  type: 'success' | 'warning' | 'info';
  title: string;
  description: string;
  value?: string;
  icon?: 'check' | 'alert' | 'trend' | 'leaf' | 'dollar';
}

interface InsightsCardProps {
  insights: Insight[];
}

const InsightsCard: React.FC<InsightsCardProps> = ({ insights }) => {
  const getIcon = (iconType?: string) => {
    switch (iconType) {
      case 'check':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'alert':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'trend':
        return <TrendingUp className="w-5 h-5 text-blue-600" />;
      case 'leaf':
        return <Leaf className="w-5 h-5 text-emerald-600" />;
      case 'dollar':
        return <DollarSign className="w-5 h-5 text-green-600" />;
      default:
        return <Lightbulb className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'info':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <Card className="bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-200 sticky top-24 shadow-lg">
      <CardHeader className="border-b border-yellow-200">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Lightbulb className="w-6 h-6 text-yellow-500 animate-pulse" />
          💡 ข้อมูลเชิงลึก
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-3 max-h-[600px] overflow-y-auto">
        {insights.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Lightbulb className="w-12 h-12 mx-auto mb-2 text-gray-400" />
            <p className="text-sm">ไม่มีข้อมูลเชิงลึก</p>
          </div>
        ) : (
          insights.map((insight) => (
            <div
              key={insight.id}
              className={`p-3 rounded-lg border ${getTypeColor(insight.type)} transition-all duration-200 hover:shadow-md`}
            >
              <div className="flex items-start gap-3">
                <div className="p-2 bg-white rounded-lg shadow-sm">
                  {getIcon(insight.icon)}
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-sm mb-1">{insight.title}</h4>
                  <p className="text-xs text-gray-700 mb-2">{insight.description}</p>
                  {insight.value && (
                    <Badge variant="secondary" className="text-xs">
                      {insight.value}
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
};

export default InsightsCard;
