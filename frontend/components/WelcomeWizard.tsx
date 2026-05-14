/**
 * 欢迎向导组件
 * 
 * 在用户首次运行应用时显示，引导用户完成基本配置：
 * 1. 欢迎页面 - 介绍应用功能
 * 2. Cookie设置 - 引导用户配置Cookie
 * 3. 下载路径设置 - 选择默认下载位置
 * 4. 完成页面 - 显示配置完成信息
 */

import { Check, ChevronLeft, ChevronRight, ExternalLink, FolderOpen, LogIn, Sparkles, X } from 'lucide-react';
import React, { useState } from 'react';
import { APP_DEFAULTS } from '../constants';
import { bridge, isGUIMode } from '../services/bridge';
import { logger } from '../services/logger';
import { AppSettings } from '../types';
import { toast } from './Toast';

interface WelcomeWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

type WizardStep = 'welcome' | 'cookie' | 'download' | 'complete';

export const WelcomeWizard: React.FC<WelcomeWizardProps> = ({ isOpen, onClose, onComplete }) => {
  const [currentStep, setCurrentStep] = useState<WizardStep>('welcome');
  const [settings, setSettings] = useState<AppSettings>({
    cookie: APP_DEFAULTS.COOKIE,
    userAgent: APP_DEFAULTS.USER_AGENT,
    downloadPath: APP_DEFAULTS.DOWNLOAD_PATH,
    maxRetries: APP_DEFAULTS.MAX_RETRIES,
    maxConcurrency: APP_DEFAULTS.MAX_CONCURRENCY,
    enableIncrementalFetch: APP_DEFAULTS.ENABLE_INCREMENTAL_FETCH,
    aria2Host: APP_DEFAULTS.ARIA2_HOST,
    aria2Port: APP_DEFAULTS.ARIA2_PORT,
    aria2Secret: APP_DEFAULTS.ARIA2_SECRET,
    enableDownloadTitle: APP_DEFAULTS.ENABLE_DOWNLOAD_TITLE,
    enableDownloadCover: APP_DEFAULTS.ENABLE_DOWNLOAD_COVER,
    downloadInterval: APP_DEFAULTS.DOWNLOAD_INTERVAL,
  });
  const [isSaving, setIsSaving] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const handleNext = () => {
    const steps: WizardStep[] = ['welcome', 'cookie', 'download', 'complete'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
    }
  };

  const handleBack = () => {
    const steps: WizardStep[] = ['welcome', 'cookie', 'download', 'complete'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
    }
  };

  const handleSkip = () => {
    // 跳过向导，使用默认配置
    onComplete();
  };

  const handleComplete = async () => {
    setIsSaving(true);
    try {
      // 如果下载路径为空，先从后端获取默认路径
      let finalSettings = { ...settings };
      if (!finalSettings.downloadPath) {
        try {
          const currentSettings = await bridge.getSettings();
          finalSettings.downloadPath = currentSettings.downloadPath;
        } catch (err) {
          console.error('获取默认路径失败:', err);
          // 如果获取失败，使用一个占位符，后端会使用默认值
          finalSettings.downloadPath = './download';
        }
      }

      // 保存配置
      await bridge.saveSettings(finalSettings);
      console.log('配置保存成功');
      // 完成向导
      onComplete();
    } catch (e) {
      console.error("Failed to save settings", e);
      const errorMsg = e instanceof Error ? e.message : String(e);
      toast.error(`配置保存失败: ${errorMsg}\n\n请稍后在设置中重新配置。`);
      // 即使保存失败也完成向导，让用户可以使用应用
      onComplete();
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
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 animate-in fade-in duration-300">
      <div className="bg-white rounded-3xl w-full max-w-lg shadow-2xl overflow-hidden transform transition-all">
        {/* 头部 */}
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gradient-to-r from-blue-500 to-purple-500">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
              <Sparkles className="text-white" size={18} />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">欢迎使用DouyinCrawler</h3>
              <p className="text-xs text-white/80">让我们开始配置您的应用</p>
            </div>
          </div>
          <button
            onClick={handleSkip}
            className="p-2 hover:bg-white/20 rounded-full text-white transition-colors"
            title="跳过向导"
          >
            <X size={20} />
          </button>
        </div>

        {/* 进度指示器 */}
        <div className="px-6 py-3 bg-gray-50/50 border-b border-gray-100">
          <div className="flex items-center justify-between">
            {['欢迎', 'Cookie', '下载路径', '完成'].map((label, index) => {
              const steps: WizardStep[] = ['welcome', 'cookie', 'download', 'complete'];
              const stepIndex = steps.indexOf(currentStep);
              const isActive = index === stepIndex;
              const isCompleted = index < stepIndex;

              return (
                <React.Fragment key={label}>
                  <div className="flex items-center gap-1.5">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold transition-all ${isActive
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                      : isCompleted
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-500'
                      }`}>
                      {isCompleted ? <Check size={12} /> : index + 1}
                    </div>
                    <span className={`text-xs font-medium ${isActive ? 'text-gray-900' : 'text-gray-500'
                      }`}>
                      {label}
                    </span>
                  </div>
                  {index < 3 && (
                    <div className={`flex-1 h-1 mx-2 rounded-full transition-all ${isCompleted ? 'bg-green-500' : 'bg-gray-200'
                      }`} />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* 内容区域 */}
        <div className="p-6 min-h-[300px]">
          {/* 欢迎页面 */}
          {currentStep === 'welcome' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl mx-auto mb-3 flex items-center justify-center">
                  <Sparkles className="text-white" size={28} />
                </div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">欢迎使用DouyinCrawler！</h2>
                <p className="text-sm text-gray-600">一个强大的抖音数据采集和下载工具</p>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-4 space-y-3">
                <h3 className="font-semibold text-gray-900 text-sm mb-2">主要功能：</h3>
                <div className="space-y-2">
                  <div className="flex items-start gap-2">
                    <div className="w-5 h-5 bg-blue-500 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check className="text-white" size={12} />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 text-sm">多种采集模式</p>
                      <p className="text-xs text-gray-600">支持用户主页、搜索、音乐、话题等</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-5 h-5 bg-purple-500 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check className="text-white" size={12} />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 text-sm">批量下载</p>
                      <p className="text-xs text-gray-600">使用Aria2实现高速多线程下载</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-5 h-5 bg-pink-500 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check className="text-white" size={12} />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 text-sm">实时日志</p>
                      <p className="text-xs text-gray-600">查看详细的运行日志，轻松排查问题</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-xs text-yellow-800">
                  <span className="font-semibold">提示：</span> 接下来我们将引导您完成基本配置，您也可以随时在设置中修改这些配置。
                </p>
              </div>
            </div>
          )}

          {/* Cookie设置页面 */}
          {currentStep === 'cookie' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">配置 Cookie</h2>
                <p className="text-gray-600">Cookie用于访问需要登录的功能，如采集用户喜欢列表</p>
              </div>

              <div>
                <div className="flex items-center justify-between mb-3">
                  <label htmlFor="wizard-cookie-input" className="block text-sm font-semibold text-gray-700">
                    Cookie 设置（可选）
                  </label>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={async () => {
                        try {
                          const text = await bridge.getClipboardText();
                          if (!text) {
                            toast.error('剪贴板为空');
                            return;
                          }
                          setSettings({ ...settings, cookie: text.trim() });
                          console.log('已粘贴Cookie');
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
                              toast.success('Cookie 获取成功！');
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
                  id="wizard-cookie-input"
                  name="cookie"
                  value={settings.cookie}
                  onChange={(e) => setSettings({ ...settings, cookie: e.target.value })}
                  placeholder="请输入 douyin.com 的 Cookie...&#10;&#10;如果暂时不需要，可以跳过此步骤，稍后在设置中配置"
                  className="w-full h-40 px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all resize-none"
                />
                <p className="mt-2 text-xs text-gray-500">
                  💡 Cookie可以让您访问需要登录的功能。如果您只需要采集公开内容，可以暂时跳过。
                </p>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <p className="text-sm text-blue-800">
                  <span className="font-semibold">提示：</span> 您可以先跳过Cookie配置，使用基本功能。需要时可以随时在设置中添加。
                </p>
              </div>
            </div>
          )}

          {/* 下载路径设置页面 */}
          {currentStep === 'download' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">设置下载路径</h2>
                <p className="text-gray-600">选择下载文件的默认保存位置</p>
              </div>

              <div>
                <label htmlFor="wizard-download-path-input" className="block text-sm font-semibold text-gray-700 mb-3">
                  默认下载路径
                </label>
                <div className="flex gap-3">
                  <input
                    id="wizard-download-path-input"
                    name="downloadPath"
                    type="text"
                    value={settings.downloadPath}
                    onChange={(e) => setSettings({ ...settings, downloadPath: e.target.value })}
                    placeholder="例如 D:\Downloads\Douyin"
                    className="flex-1 px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                  />
                  <button
                    onClick={handleSelectFolder}
                    className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-xl flex items-center gap-2 transition-all shadow-lg shadow-blue-200"
                    title="选择文件夹"
                  >
                    <FolderOpen size={18} />
                    <span className="font-medium">浏览</span>
                  </button>
                </div>
                <p className="mt-2 text-xs text-gray-500">
                  💡 如果不设置，将使用默认路径：程序所在目录/download
                </p>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-6">
                <h3 className="font-semibold text-gray-900 mb-3">其他配置：</h3>
                <div className="space-y-3 text-sm text-gray-700">
                  <div className="flex justify-between items-center">
                    <span>最大重试次数：</span>
                    <span className="font-semibold text-blue-600">3 次</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>同时下载任务数：</span>
                    <span className="font-semibold text-purple-600">5 个</span>
                  </div>
                  <p className="text-xs text-gray-500 pt-2 border-t border-gray-200">
                    这些参数已设置为推荐值，您可以稍后在设置中调整
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* 完成页面 */}
          {currentStep === 'complete' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                  <Check className="text-white" size={40} />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">配置完成！</h2>
                <p className="text-gray-600">您已成功完成初始配置，现在可以开始使用了</p>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-6 space-y-4">
                <h3 className="font-semibold text-gray-900 mb-3">配置摘要：</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check className="text-white" size={14} />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">Cookie</p>
                      <p className="text-gray-600">
                        {settings.cookie ? '已配置 ✓' : '未配置（可稍后添加）'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-purple-500 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check className="text-white" size={14} />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">下载路径</p>
                      <p className="text-gray-600 break-all">
                        {settings.downloadPath || '使用默认路径'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                <p className="text-sm text-green-800">
                  <span className="font-semibold">提示：</span> 您可以随时在设置中修改这些配置。点击"开始使用"即可进入应用主界面。
                </p>
              </div>
            </div>
          )}
        </div>

        {/* 底部按钮 */}
        <div className="px-6 py-4 bg-gray-50/50 border-t border-gray-100 flex justify-between">
          <div>
            {currentStep !== 'welcome' && currentStep !== 'complete' && (
              <button
                onClick={handleBack}
                className="px-5 py-2.5 rounded-xl text-gray-600 font-medium hover:bg-gray-200 transition-colors text-sm flex items-center gap-2"
              >
                <ChevronLeft size={16} />
                上一步
              </button>
            )}
          </div>
          <div className="flex gap-3">
            {currentStep !== 'complete' && (
              <button
                onClick={handleSkip}
                className="px-5 py-2.5 rounded-xl text-gray-600 font-medium hover:bg-gray-200 transition-colors text-sm"
              >
                跳过向导
              </button>
            )}
            {currentStep === 'complete' ? (
              <button
                onClick={handleComplete}
                disabled={isSaving}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-medium shadow-lg shadow-green-200 active:scale-95 transition-all text-sm flex items-center gap-2"
              >
                <Check size={16} />
                {isSaving ? '保存中...' : '开始使用'}
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium shadow-lg shadow-blue-200 active:scale-95 transition-all text-sm flex items-center gap-2"
              >
                下一步
                <ChevronRight size={16} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
