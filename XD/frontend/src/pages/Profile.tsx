import { useState, useEffect, FormEvent } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useProvinces } from '@/hooks/useProvinces';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { User, Mail, Lock, Save, AlertCircle, CheckCircle, MapPin } from 'lucide-react';
import MapNavbar from '@/components/MapNavbar';
import { validateProfileData, VALID_SOIL_TYPES, VALID_WATER_LEVELS, VALID_BUDGET_LEVELS, VALID_RISK_LEVELS } from '@/utils/validation';

const API_BASE = 'http://localhost:8000';

const Profile = () => {
  const { user } = useAuth();
  const { provinces, loading: provincesLoading, error: provincesError } = useProvinces();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  
  // Form states
  const [email, setEmail] = useState(user?.email || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  // Profile data states
  const [profileData, setProfileData] = useState({
    full_name: '',
    province: '',
    water_availability: '',
    budget_level: '',
    experience_crops: '',
    risk_tolerance: '',
    time_constraint: 0,
    preference: '',
    soil_type: ''
  });

  // Fetch user profile on load
  useEffect(() => {
    const fetchProfile = async () => {
      if (!user?.id) return;
      
      try {
        const response = await fetch(`${API_BASE}/api/user/profile/${user.id}`);
        const data = await response.json();
        
        if (data.success) {
          setProfileData({
            full_name: data.user.full_name || '',
            province: data.user.province || '',
            water_availability: data.user.water_availability || '',
            budget_level: data.user.budget_level || '',
            experience_crops: data.user.experience_crops || '',
            risk_tolerance: data.user.risk_tolerance || '',
            time_constraint: data.user.time_constraint || 0,
            preference: data.user.preference || '',
            soil_type: data.user.soil_type || ''
          });
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
      }
    };
    
    fetchProfile();
  }, [user?.id]);

  const handleUpdateEmail = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    try {
      const response = await fetch(`${API_BASE}/api/user/email`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user?.id,
          new_email: email
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'เกิดข้อผิดพลาด');
      }
      
      setMessage({ 
        type: 'success', 
        text: 'อีเมลถูกอัพเดทเรียบร้อยแล้ว!' 
      });
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.message || 'เกิดข้อผิดพลาดในการอัพเดทอีเมล' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdatePassword = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    // Validation
    if (newPassword.length < 6) {
      setMessage({ type: 'error', text: 'รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร' });
      setIsLoading(false);
      return;
    }

    if (newPassword !== confirmPassword) {
      setMessage({ type: 'error', text: 'รหัสผ่านไม่ตรงกัน' });
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/user/password`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user?.id,
          new_password: newPassword
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'เกิดข้อผิดพลาด');
      }
      
      setMessage({ type: 'success', text: 'รหัสผ่านถูกเปลี่ยนเรียบร้อยแล้ว!' });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.message || 'เกิดข้อผิดพลาดในการเปลี่ยนรหัสผ่าน' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateProfile = async (e: FormEvent) => {
    e.preventDefault();
    setMessage(null);

    // Client-side validation
    const validation = validateProfileData(profileData, provinces);
    if (!validation.isValid) {
      setMessage({ 
        type: 'error', 
        text: validation.errors.join(', ')
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/user/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user?.id,
          ...profileData,
          time_constraint: profileData.time_constraint || null
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'เกิดข้อผิดพลาด');
      }
      
      setMessage({ type: 'success', text: 'อัพเดทข้อมูลส่วนตัวเรียบร้อยแล้ว!' });
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.message || 'เกิดข้อผิดพลาดในการอัพเดทข้อมูล' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50">
        <MapNavbar />
        <div className="container mx-auto px-4 py-8">
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              กรุณาเข้าสู่ระบบก่อนเข้าถึงหน้านี้
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <MapNavbar />
      
      <div className="container max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">ข้อมูลส่วนตัว</h1>
          <p className="text-gray-600">จัดการข้อมูลบัญชีและความปลอดภัยของคุณ</p>
        </div>

        {message && (
          <Alert className={`mb-6 ${message.type === 'success' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
            {message.type === 'success' ? (
              <CheckCircle className="h-4 w-4 text-green-600" />
            ) : (
              <AlertCircle className="h-4 w-4 text-red-600" />
            )}
            <AlertDescription className={message.type === 'success' ? 'text-green-800' : 'text-red-800'}>
              {message.text}
            </AlertDescription>
          </Alert>
        )}

        <div className="grid gap-6">
          {/* Profile Information Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5 text-emerald-600" />
                ข้อมูลส่วนตัว
              </CardTitle>
              <CardDescription>
                แก้ไขข้อมูลโปรไฟล์ของคุณ
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="full_name">ชื่อ-นามสกุล</Label>
                    <Input
                      id="full_name"
                      value={profileData.full_name}
                      onChange={(e) => setProfileData({...profileData, full_name: e.target.value})}
                      placeholder="ชื่อ-นามสกุล"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="province" className="flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      จังหวัด
                      {provincesLoading && <span className="text-xs text-gray-400">(กำลังโหลด...)</span>}
                      {!provincesLoading && provinces.length > 0 && (
                        <span className="text-xs text-gray-400">({provinces.length} จังหวัด)</span>
                      )}
                    </Label>
                    {provincesLoading ? (
                      <div className="w-full p-2 border rounded-md text-sm text-gray-500 bg-gray-50">
                        กำลังโหลดจังหวัด...
                      </div>
                    ) : (
                      <select
                        id="province"
                        value={profileData.province}
                        onChange={(e) => setProfileData({...profileData, province: e.target.value})}
                        className="w-full p-2 border rounded-md"
                      >
                        <option value="">เลือกจังหวัด</option>
                        {provinces.map((prov) => (
                          <option key={prov} value={prov}>{prov}</option>
                        ))}
                      </select>
                    )}
                    {provincesError && (
                      <p className="text-xs text-red-500">{provincesError}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="water">แหล่งน้ำ</Label>
                    <select
                      id="water"
                      value={profileData.water_availability}
                      onChange={(e) => setProfileData({...profileData, water_availability: e.target.value})}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="">เลือก...</option>
                      {VALID_WATER_LEVELS.map((level) => (
                        <option key={level} value={level}>{level}</option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="budget">งบประมาณ</Label>
                    <select
                      id="budget"
                      value={profileData.budget_level}
                      onChange={(e) => setProfileData({...profileData, budget_level: e.target.value})}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="">เลือก...</option>
                      {VALID_BUDGET_LEVELS.map((level) => (
                        <option key={level} value={level}>{level}</option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="soil">ประเภทดิน</Label>
                    <select
                      id="soil"
                      value={profileData.soil_type}
                      onChange={(e) => setProfileData({...profileData, soil_type: e.target.value})}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="">เลือก...</option>
                      {VALID_SOIL_TYPES.map((type) => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="risk">ความเสี่ยงที่รับได้</Label>
                    <select
                      id="risk"
                      value={profileData.risk_tolerance}
                      onChange={(e) => setProfileData({...profileData, risk_tolerance: e.target.value})}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="">เลือก...</option>
                      {VALID_RISK_LEVELS.map((level) => (
                        <option key={level} value={level}>{level}</option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="experience">พืชที่เคยปลูก</Label>
                    <Input
                      id="experience"
                      value={profileData.experience_crops}
                      onChange={(e) => setProfileData({...profileData, experience_crops: e.target.value})}
                      placeholder="เช่น ข้าว, พริก, มะเขือเทศ (คั่นด้วยจุลภาค)"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="time">เวลาว่าง (ชั่วโมง/สัปดาห์)</Label>
                    <Input
                      id="time"
                      type="number"
                      value={profileData.time_constraint || ''}
                      onChange={(e) => setProfileData({...profileData, time_constraint: parseInt(e.target.value) || 0})}
                      placeholder="เช่น 20"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="preference">ความชอบ</Label>
                    <select
                      id="preference"
                      value={profileData.preference}
                      onChange={(e) => setProfileData({...profileData, preference: e.target.value})}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="">เลือก...</option>
                      <option value="ผลตอบแทนสูง">ผลตอบแทนสูง</option>
                      <option value="ดูแลง่าย">ดูแลง่าย</option>
                      <option value="ขายได้เร็ว">ขายได้เร็ว</option>
                      <option value="ปลอดภัย">ปลอดภัย/เสี่ยงต่ำ</option>
                    </select>
                  </div>
                </div>
                
                <Button 
                  type="submit" 
                  disabled={isLoading}
                  className="bg-emerald-600 hover:bg-emerald-700"
                >
                  <Save className="w-4 h-4 mr-2" />
                  บันทึกข้อมูลส่วนตัว
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Account Information Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="w-5 h-5 text-emerald-600" />
                อีเมล
              </CardTitle>
              <CardDescription>
                เปลี่ยนอีเมลสำหรับเข้าสู่ระบบ
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateEmail} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">อีเมลใหม่</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    required
                  />
                  <p className="text-xs text-gray-500">
                    อีเมลปัจจุบัน: {user.email}
                  </p>
                </div>
                
                <Button 
                  type="submit" 
                  disabled={isLoading || email === user.email}
                  className="bg-emerald-600 hover:bg-emerald-700"
                >
                  <Save className="w-4 h-4 mr-2" />
                  บันทึกอีเมล
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Password Change Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="w-5 h-5 text-emerald-600" />
                เปลี่ยนรหัสผ่าน
              </CardTitle>
              <CardDescription>
                อัพเดทรหัสผ่านของคุณเพื่อความปลอดภัย
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdatePassword} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="new-password">รหัสผ่านใหม่</Label>
                  <Input
                    id="new-password"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    minLength={6}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirm-password">ยืนยันรหัสผ่านใหม่</Label>
                  <Input
                    id="confirm-password"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    minLength={6}
                  />
                </div>

                <div className="pt-2">
                  <Button 
                    type="submit" 
                    disabled={isLoading || !newPassword || !confirmPassword}
                    className="bg-emerald-600 hover:bg-emerald-700"
                  >
                    <Lock className="w-4 h-4 mr-2" />
                    เปลี่ยนรหัสผ่าน
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Account Info Display */}
          <Card className="bg-gradient-to-br from-emerald-50 to-green-50 border-emerald-200">
            <CardHeader>
              <CardTitle className="text-emerald-800">ข้อมูลบัญชี</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">User ID:</span>
                <span className="text-sm font-mono text-gray-800">{user.id}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">อีเมลปัจจุบัน:</span>
                <span className="text-sm font-medium text-gray-800">{user.email}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">ชื่อผู้ใช้:</span>
                <span className="text-sm text-gray-800">{user.username}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Profile;
