
import { ChevronDown, ChevronUp, ExternalLink, FolderOpen, LogIn, Save, X } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { APP_DEFAULTS } from '../constants';
import { aria2Service } from '../services/aria2Service';
import { bridge, isGUIMode } from '../services/bridge';
import { logger } from '../services/logger';
import { AppSettings } from '../types';
import { toast } from './Toast';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

// Helper component for styled number input
interface NumberInputProps {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (val: number) => void;
}

const NumberInput: React.FC<NumberInputProps> = ({ label, value, min, max, onChange }) => {
  const inputId = `input-${label.replace(/\s+/g, '-').toLowerCase()}`;

  const handleIncrement = () => {
    if (value < max) onChange(value + 1);
  };

  const handleDecrement = () => {
    if (value > min) onChange(value - 1);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value);
    if (!isNaN(val)) {
      // Allow typing, clamp on blur if needed, but here we just update
      // Ideally we clamp here or let user type freely but valid
      onChange(val);
    } else if (e.target.value === '') {
      onChange(0);
    }
  };

  return (
    <div>
      <label htmlFor={inputId} className="block text-sm font-semibold text-gray-700 mb-2">
        {label}
      </label>
      <div className="relative group">
        <input
          id={inputId}
          name={inputId}
          type="number"
          min={min}
          max={max}
          value={value}
          onChange={handleChange}
          className="w-full pl-4 pr-10 py-2.5 border border-gray-200 rounded-xl bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
        />
        <div className="absolute right-0 top-0 bottom-0 w-8 flex flex-col border-l border-gray-200">
          <button
            onClick={handleIncrement}
            disabled={value >= max}
            className="flex-1 flex items-center justify-center hover:bg-gray-100 active:bg-gray-200 text-gray-500 rounded-tr-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronUp size={12} />
          </button>
          <div className="h-px bg-gray-200"></div>
          <button
            onClick={handleDecrement}
            disabled={value <= min}
            className="flex-1 flex items-center justify-center hover:bg-gray-100 active:bg-gray-200 text-gray-500 rounded-br-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronDown size={12} />
          </button>
        </div>
      </div>
    </div>
  );
};

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState<AppSettings>({
    cookie: APP_DEFAULTS.COOKIE,
    userAgent: APP_DEFAULTS.USER_AGENT,
    downloadPath: APP_DEFAULTS.DOWNLOAD_PATH,
    maxRetries: APP_DEFAULTS.MAX_RETRIES,
    maxConcurrency: APP_DEFAULTS.MAX_CONCURRENCY,
    enableIncrementalFetch: APP_DEFAULTS.ENABLE_INCREMENTAL_FETCH,
    aria2Host: APP_DEFAULTS.ARIA2_HOST,
    aria2Port: APP_DEFAULTS.ARIA2_PORT,
    aria2Secret: APP_DEFAULTS.ARIA2_SECRET
  });
  const [isSaving, setIsSaving] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [errors, setErrors] = useState<Partial<Record<keyof AppSettings, string>>>({});

  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen]);

  const loadSettings = async () => {
    try {
      const data = await bridge.getSettings();
      setSettings(data);
    } catch (e) {
      console.error("Failed to load settings", e);
    }
  };

  // 验证设置
  const validateSettings = (): boolean => {
    const newErrors: Partial<Record<keyof AppSettings, string>> = {};

    // 验证下载路径
    if (!settings.downloadPath) {
      newErrors.downloadPath = "请选择下载路径";
    } else {
      // 检查路径是否有效（支持 Windows 和 Linux/Unix 风格）
      // Windows: C:\path, D:\folder\subfolder
      // Linux: /path, ~/path, folder/subfolder
      const pathRegex = /^(~|([a-zA-Z]:))?([\\/][^<>:"|?*\n\r]+)+[\\/]?$|^\.?[\\/][^<>:"|?*\n\r]+$/;
      if (!pathRegex.test(settings.downloadPath)) {
        newErrors.downloadPath = "无效的路径格式";
      }
    }

    // 验证最大重试次数
    if (settings.maxRetries < 1 || settings.maxRetries > 10) {
      newErrors.maxRetries = "最大重试次数必须在1-10之间";
    }

    // 验证同时下载任务数
    if (settings.maxConcurrency < 1 || settings.maxConcurrency > 10) {
      newErrors.maxConcurrency = "同时下载任务数必须在1-10之间";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    // 验证设置
    if (!validateSettings()) {
      toast.error('请检查配置项是否正确');
      return;
    }

    setIsSaving(true);
    try {
      await bridge.saveSettings(settings);
      logger.success('✓ 配置保存成功');

      // 即时更新Aria2配置
      try {
        await aria2Service.updateGlobalOptions({
          'max-concurrent-downloads': settings.maxConcurrency.toString(),
          'max-tries': settings.maxRetries.toString(),
        });
      } catch (err) {
        // 错误已在aria2Service中处理和记录
      }

      toast.success('配置保存成功');
      // 等待后端日志传递到前端（100ms足够）
      await new Promise(resolve => setTimeout(resolve, 100));
      // 关闭弹窗
      onClose();
    } catch (e) {
      // 保存失败时在日志和Toast中输出
      const errorMsg = e instanceof Error ? e.message : String(e);
      logger.error(`✗ 配置保存失败: ${errorMsg}`);
      toast.error(`配置保存失败: ${errorMsg}`);
      console.error("Failed to save settings", e);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSelectFolder = async () => {
    try {
      const path = await bridge.selectFolder();
      if (path) {
        setSettings(prev => ({ ...prev, downloadPath: path }));
      }
    } catch (e) {
      console.error("Failed to select folder", e);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden transform transition-all scale-100"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
          <h3 className="text-lg font-bold text-gray-800">系统设置</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-200 rounded-full text-gray-500 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-5">
          {/* Cookie Setting */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label htmlFor="cookie-input" className="block text-sm font-semibold text-gray-700">
                Cookie 设置
              </label>
              <div className="flex items-center gap-2">
                <button
                  onClick={async () => {
                    try {
                      const text = await bridge.getClipboardText();
                      if (!text) {
                        toast.info('剪贴板为空');
                        return;
                      }
                      setSettings({ ...settings, cookie: text.trim() });
                      if (errors.cookie) {
                        setErrors(prev => {
                          const newErrors = { ...prev };
                          delete newErrors.cookie;
                          return newErrors;
                        });
                      }
                      toast.success('已粘贴剪贴板内容');
                    } catch (err) {
                      console.error('粘贴失败:', err);
                      toast.error('粘贴失败，请手动输入');
                    }
                  }}
                  className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg flex items-center gap-1 transition-colors"
                  title="一键粘贴剪贴板内容"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  粘贴
                </button>
                {isGUIMode() ? (
                  <button
                    onClick={async () => {
                      setIsLoggingIn(true);
                      toast.info('正在打开登录窗口，请完成登录...');
                      try {
                        const result = await bridge.cookieLogin();
                        if (result.success) {
                          setSettings(prev => ({ 
                            ...prev, 
                            cookie: result.cookie,
                            userAgent: result.user_agent || prev.userAgent
                          }));
                          if (errors.cookie) {
                            setErrors(prev => {
                              const newErrors = { ...prev };
                              delete newErrors.cookie;
                              return newErrors;
                            });
                          }
                          toast.success('Cookie 获取成功！请点击保存配置');
                          logger.success('✓ 通过登录获取 Cookie 成功');
                        } else {
                          toast.error(result.error || '获取失败');
                          logger.warn(`✗ Cookie 获取失败: ${result.error}`);
                        }
                      } catch (err) {
                        console.error('登录获取失败:', err);
                        toast.error('登录获取失败，请手动输入');
                      } finally {
                        setIsLoggingIn(false);
                      }
                    }}
                    disabled={isLoggingIn}
                    className="text-xs bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white px-3 py-1.5 rounded-lg flex items-center gap-1 transition-colors"
                    title="打开抖音登录窗口获取 Cookie"
                  >
                    <LogIn size={12} />
                    {isLoggingIn ? '登录中...' : '登录获取'}
                  </button>
                ) : (
                  <button
                    disabled={true}
                    className="text-xs bg-gray-400 text-white px-3 py-1.5 rounded-lg flex items-center gap-1 cursor-not-allowed opacity-60"
                    title="仅 GUI 模式支持"
                  >
                    <LogIn size={12} />
                    仅GUI模式
                  </button>
                )}
                <button
                  onClick={() => bridge.openExternal('https://github.com/erma0/douyin/blob/main/USAGE.md#cookie%E8%8E%B7%E5%8F%96')}
                  className="text-xs text-blue-600 hover:text-blue-700 hover:underline flex items-center gap-1 transition-colors"
                  title="查看获取 Cookie 的详细教程"
                >
                  手动获取?
                  <ExternalLink size={12} />
                </button>
              </div>
            </div>
            <textarea
              id="cookie-input"
              name="cookie"
              value={settings.cookie}
              onChange={(e) => {
                setSettings({ ...settings, cookie: e.target.value });
                // 清除cookie错误
                if (errors.cookie) {
                  setErrors(prev => {
                    const newErrors = { ...prev };
                    delete newErrors.cookie;
                    return newErrors;
                  });
                }
              }}
              placeholder="请输入 douyin.com 的 Cookie..."
              className={`w-full h-32 px-4 py-3 border rounded-xl bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all resize-none ${errors.cookie ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : 'border-gray-200 focus:border-blue-500'
                }`}
            />
            {errors.cookie && (
              <p className="mt-1.5 text-xs text-red-500">{errors.cookie}</p>
            )}
            <p className="mt-1.5 text-xs text-gray-400">
              需要登录 Cookie 才能使用。
            </p>
          </div>

          {/* Download Path */}
          <div>
            <label htmlFor="download-path-input" className="block text-sm font-semibold text-gray-700 mb-2">
              默认下载路径
            </label>
            <div className="flex gap-2">
              <input
                id="download-path-input"
                name="downloadPath"
                type="text"
                value={settings.downloadPath}
                onChange={(e) => {
                  setSettings({ ...settings, downloadPath: e.target.value });
                  // 清除路径错误
                  if (errors.downloadPath) {
                    setErrors(prev => {
                      const newErrors = { ...prev };
                      delete newErrors.downloadPath;
                      return newErrors;
                    });
                  }
                }}
                placeholder="例如 D:\Downloads"
                className={`flex-1 px-4 py-2.5 border rounded-xl bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all ${errors.downloadPath ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : 'border-gray-200 focus:border-blue-500'
                  }`}
              />
              <button
                onClick={handleSelectFolder}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl flex items-center transition-colors"
                title="选择文件夹"
              >
                <FolderOpen size={18} />
              </button>
            </div>
            {errors.downloadPath && (
              <p className="mt-1.5 text-xs text-red-500">{errors.downloadPath}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Max Retries */}
            <div>
              <NumberInput
                label="最大重试次数"
                value={settings.maxRetries}
                min={1}
                max={10}
                onChange={(val) => {
                  setSettings({ ...settings, maxRetries: val });
                  // 清除错误
                  if (errors.maxRetries) {
                    setErrors(prev => {
                      const newErrors = { ...prev };
                      delete newErrors.maxRetries;
                      return newErrors;
                    });
                  }
                }}
              />
              {errors.maxRetries && (
                <p className="mt-1.5 text-xs text-red-500">{errors.maxRetries}</p>
              )}
            </div>

            {/* Max Concurrency */}
            <div>
              <NumberInput
                label="同时下载任务数"
                value={settings.maxConcurrency}
                min={1}
                max={10}
                onChange={(val) => {
                  setSettings({ ...settings, maxConcurrency: val });
                  // 清除错误
                  if (errors.maxConcurrency) {
                    setErrors(prev => {
                      const newErrors = { ...prev };
                      delete newErrors.maxConcurrency;
                      return newErrors;
                    });
                  }
                }}
              />
              {errors.maxConcurrency && (
                <p className="mt-1.5 text-xs text-red-500">{errors.maxConcurrency}</p>
              )}
            </div>
          </div>

          {/* 增量采集开关 */}
          <div>
            <label className="flex items-center justify-between cursor-pointer group">
              <div>
                <div className="text-sm font-semibold text-gray-700 mb-1">增量采集</div>
                <p className="text-xs text-gray-400">
                  仅采集新作品，自动跳过已采集内容（仅用户主页）
                </p>
              </div>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={settings.enableIncrementalFetch}
                  onChange={(e) => setSettings({ ...settings, enableIncrementalFetch: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-500/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </div>
            </label>
          </div>
        </div>

        <div className="px-6 py-4 bg-gray-50/50 border-t border-gray-100 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-5 py-2.5 rounded-xl text-gray-600 font-medium hover:bg-gray-200 transition-colors text-sm"
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white font-medium shadow-md shadow-blue-200 active:scale-95 transition-all text-sm flex items-center gap-2"
          >
            <Save size={16} />
            {isSaving ? '保存中...' : '保存配置'}
          </button>
        </div>
      </div>
    </div>
  );
};
