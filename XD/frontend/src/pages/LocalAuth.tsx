import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useProvinces } from '@/hooks/useProvinces';
import { validateProfileData, VALID_SOIL_TYPES } from '@/utils/validation';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const LocalAuth = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  // Load provinces from API
  const { provinces, loading: provincesLoading, error: provincesError } = useProvinces();

  // Login form
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form - Basic info
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerUsername, setRegisterUsername] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerFullName, setRegisterFullName] = useState('');

  // Register form - Profile info
  const [province, setProvince] = useState('');
  const [waterAvailability, setWaterAvailability] = useState('');
  const [budgetLevel, setBudgetLevel] = useState('');
  const [experienceCrops, setExperienceCrops] = useState('');
  const [riskTolerance, setRiskTolerance] = useState('');
  const [timeConstraint, setTimeConstraint] = useState('');
  const [preference, setPreference] = useState('');
  const [soilType, setSoilType] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: loginEmail,
          password: loginPassword
        })
      });

      const data = await response.json();

      if (data.success) {
        // Store token in localStorage
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));

        toast({
          title: 'เข้าสู่ระบบสำเร็จ!',
          description: `ยินดีต้อนรับ ${data.user.username}`,
        });

        navigate('/');
      } else {
        toast({
          title: 'เข้าสู่ระบบไม่สำเร็จ',
          description: data.message,
          variant: 'destructive',
        });
      }
    } catch (error: any) {
      toast({
        title: 'เกิดข้อผิดพลาด',
        description: error.message || 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation
    const profileData = {
      province: province || undefined,
      soil_type: soilType || undefined,
      water_availability: waterAvailability || undefined,
      budget_level: budgetLevel || undefined,
      risk_tolerance: riskTolerance || undefined
    };

    const validation = validateProfileData(profileData, provinces);
    if (!validation.isValid) {
      toast({
        title: 'ข้อมูลไม่ถูกต้อง',
        description: validation.errors.join(', '),
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: registerEmail,
          username: registerUsername,
          password: registerPassword,
          full_name: registerFullName,
          province: province || null,
          water_availability: waterAvailability || null,
          budget_level: budgetLevel || null,
          experience_crops: experienceCrops ? experienceCrops.split(',').map(c => c.trim()) : null,
          risk_tolerance: riskTolerance || null,
          time_constraint: timeConstraint ? parseInt(timeConstraint) : null,
          preference: preference || null,
          soil_type: soilType || null
        })
      });

      const data = await response.json();

      if (data.success) {
        // Store token in localStorage
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));

        toast({
          title: 'สมัครสมาชิกสำเร็จ!',
          description: 'คุณสามารถใช้งานระบบได้เลย',
        });

        navigate('/');
      } else {
        toast({
          title: 'สมัครสมาชิกไม่สำเร็จ',
          description: data.message,
          variant: 'destructive',
        });
      }
    } catch (error: any) {
      toast({
        title: 'เกิดข้อผิดพลาด',
        description: error.message || 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 ">
      <Card className="w-full max-w-md shadow-2xl border-0 rounded-3xl overflow-hidden">
        <CardHeader className="text-center pb-4 pt-10">
          <div className="flex justify-center mb-6">
            <div className=" p-4 ">
              <img
                src="/Farmme_ml/XD/frontend/dist/logo.png"
                alt="FarmMe Logo"
                className="h-16 w-auto"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent className="px-8 pb-8">
          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-gray-100 p-1.5 rounded-2xl mb-6">
              <TabsTrigger
                value="login"
                className="data-[state=active]:bg-white data-[state=active]:shadow-md rounded-xl transition-all duration-200"
              >
                เข้าสู่ระบบ
              </TabsTrigger>
              <TabsTrigger
                value="register"
                className="data-[state=active]:bg-white data-[state=active]:shadow-md rounded-xl transition-all duration-200"
              >
                สมัครสมาชิก
              </TabsTrigger>
            </TabsList>

            {/* Login Tab */}
            <TabsContent value="login" className="mt-2">
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    อีเมล
                  </label>
                  <Input
                    type="email"
                    placeholder="your@email.com"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    required
                    className="rounded-2xl border-gray-200 focus:border-emerald-400 focus:ring-emerald-400 h-12"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    รหัสผ่าน
                  </label>
                  <Input
                    type="password"
                    placeholder="••••••••"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    required
                    className="rounded-2xl border-gray-200 focus:border-emerald-400 focus:ring-emerald-400 h-12"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white font-medium h-12 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200 mt-6"
                  disabled={loading}
                >
                  {loading ? 'กำลังเข้าสู่ระบบ...' : 'เข้าสู่ระบบ'}
                </Button>
              </form>
            </TabsContent>

            {/* Register Tab */}
            <TabsContent value="register" className="mt-2">
              <form onSubmit={handleRegister} className="space-y-3 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">อีเมล</label>
                  <Input
                    type="email"
                    placeholder="your@email.com"
                    value={registerEmail}
                    onChange={(e) => setRegisterEmail(e.target.value)}
                    required
                    className="rounded-2xl h-11"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">ชื่อผู้ใช้</label>
                  <Input
                    type="text"
                    placeholder="username"
                    value={registerUsername}
                    onChange={(e) => setRegisterUsername(e.target.value)}
                    required
                    className="rounded-2xl h-11"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">ชื่อ-นามสกุล</label>
                  <Input
                    type="text"
                    placeholder="ชื่อ-นามสกุล (ไม่บังคับ)"
                    value={registerFullName}
                    onChange={(e) => setRegisterFullName(e.target.value)}
                    className="rounded-2xl h-11"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">รหัสผ่าน</label>
                  <Input
                    type="password"
                    placeholder="••••••••"
                    value={registerPassword}
                    onChange={(e) => setRegisterPassword(e.target.value)}
                    required
                    minLength={6}
                    className="rounded-2xl h-11"
                  />
                </div>

                {/* Profile Information */}
                <div className="pt-3 mt-3 border-t border-gray-200">
                  <p className="text-xs font-medium text-gray-500 mb-3">ข้อมูลเพิ่มเติม (ไม่บังคับ)</p>

                  <div className="space-y-2.5">
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-gray-600">จังหวัด</label>
                      {provincesLoading ? (
                        <div className="w-full px-3 py-2 border rounded-2xl text-sm text-gray-400 bg-gray-50 h-11 flex items-center">
                          กำลังโหลด...
                        </div>
                      ) : (
                        <select
                          value={province}
                          onChange={(e) => setProvince(e.target.value)}
                          className="w-full px-3 py-2 border rounded-2xl text-sm h-11 bg-white"
                        >
                          <option value="">เลือกจังหวัด</option>
                          {provinces.map((prov) => (
                            <option key={prov} value={prov}>{prov}</option>
                          ))}
                        </select>
                      )}
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-gray-600">ประเภทดิน</label>
                      <select
                        value={soilType}
                        onChange={(e) => setSoilType(e.target.value)}
                        className="w-full px-3 py-2 border rounded-2xl text-sm h-11 bg-white"
                      >
                        <option value="">เลือกประเภทดิน</option>
                        {VALID_SOIL_TYPES.map((type) => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-gray-600">แหล่งน้ำ</label>
                      <select
                        value={waterAvailability}
                        onChange={(e) => setWaterAvailability(e.target.value)}
                        className="w-full px-3 py-2 border rounded-2xl text-sm h-11 bg-white"
                      >
                        <option value="">เลือกแหล่งน้ำ</option>
                        <option value="สูง">สูง</option>
                        <option value="ปานกลาง">ปานกลาง</option>
                        <option value="ต่ำ">ต่ำ</option>
                      </select>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-gray-600">งบประมาณ</label>
                      <select
                        value={budgetLevel}
                        onChange={(e) => setBudgetLevel(e.target.value)}
                        className="w-full px-3 py-2 border rounded-2xl text-sm h-11 bg-white"
                      >
                        <option value="">เลือกงบประมาณ</option>
                        <option value="สูง">สูง</option>
                        <option value="ปานกลาง">ปานกลาง</option>
                        <option value="ต่ำ">ต่ำ</option>
                      </select>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-gray-600">ความเสี่ยง</label>
                      <select
                        value={riskTolerance}
                        onChange={(e) => setRiskTolerance(e.target.value)}
                        className="w-full px-3 py-2 border rounded-2xl text-sm h-11 bg-white"
                      >
                        <option value="">เลือกความเสี่ยง</option>
                        <option value="สูง">สูง</option>
                        <option value="ปานกลาง">ปานกลาง</option>
                        <option value="ต่ำ">ต่ำ</option>
                      </select>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-gray-600">พืชที่มีประสบการณ์</label>
                      <Input
                        type="text"
                        placeholder="ข้าว, ข้าวโพด"
                        value={experienceCrops}
                        onChange={(e) => setExperienceCrops(e.target.value)}
                        className="text-sm rounded-2xl h-11"
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-gray-600">ระยะเวลา (เดือน)</label>
                      <Input
                        type="number"
                        placeholder="6"
                        value={timeConstraint}
                        onChange={(e) => setTimeConstraint(e.target.value)}
                        className="text-sm rounded-2xl h-11"
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-gray-600">ความต้องการ</label>
                      <select
                        value={preference}
                        onChange={(e) => setPreference(e.target.value)}
                        className="w-full px-3 py-2 border rounded-2xl text-sm h-11 bg-white"
                      >
                        <option value="">เลือกความต้องการ</option>
                        <option value="ผลผลิตสูง">ผลผลิตสูง</option>
                        <option value="ราคาดี">ราคาดี</option>
                        <option value="ต้นทุนต่ำ">ต้นทุนต่ำ</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white font-medium h-12 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200 mt-4"
                  disabled={loading}
                >
                  {loading ? 'กำลังสมัครสมาชิก...' : 'สมัครสมาชิก'}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #d1d5db;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #9ca3af;
        }
      `}</style>
    </div>
  );
};

export default LocalAuth;
