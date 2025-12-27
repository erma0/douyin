import React, { useState, useRef, useEffect } from 'react';
import { ChevronUp } from 'lucide-react';

export interface FilterSettings extends Record<string, string> {
  sort_type: string;      // 排序依据: 0综合 2最新 1最多点赞
  publish_time: string;   // 发布时间: 0不限 1一天内 7一周内 180半年内
  filter_duration: string; // 视频时长: ""不限 "0-1"一分钟以下 "1-5"1-5分钟 "5-10000"5分钟以上
  search_range: string;   // 搜索范围: 0不限 3关注的人 1最近看过 2还未看过
}

interface SearchFilterProps {
  filters: FilterSettings;
  onFilterChange: (filters: FilterSettings) => void;
}

export const SearchFilter: React.FC<SearchFilterProps> = ({
  filters,
  onFilterChange,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [localFilters, setLocalFilters] = useState<FilterSettings>(filters);
  const menuRef = useRef<HTMLDivElement>(null);

  // 点击外部关闭
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
    return undefined;
  }, [isOpen]);

  const handleFilterChange = (key: keyof FilterSettings, value: string) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const sortOptions = [
    { title: '综合排序', value: '0' },
    { title: '最新发布', value: '2' },
    { title: '最多点赞', value: '1' },
  ];

  const timeOptions = [
    { title: '不限', value: '0' },
    { title: '一天内', value: '1' },
    { title: '一周内', value: '7' },
    { title: '半年内', value: '180' },
  ];

  const durationOptions = [
    { title: '不限', value: '' },
    { title: '1分钟以下', value: '0-1' },
    { title: '1-5分钟', value: '1-5' },
    { title: '5分钟以上', value: '5-10000' },
  ];

  const rangeOptions = [
    { title: '不限', value: '0' },
    { title: '关注的人', value: '3' },
    { title: '最近看过', value: '1' },
    { title: '还未看过', value: '2' },
  ];

  const FilterSection = ({
    title,
    options,
    value,
    onChange,
  }: {
    title: string;
    options: { title: string; value: string }[];
    value: string;
    onChange: (value: string) => void;
  }) => (
    <div className="mb-4 last:mb-0">
      <h3 className="text-xs font-medium text-gray-500 mb-2">{title}</h3>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option.value}
            onClick={() => onChange(option.value)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              value === option.value
                ? 'bg-blue-500 text-white shadow-md shadow-blue-500/20'
                : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100 hover:border-gray-300'
            }`}
          >
            {option.title}
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="relative" ref={menuRef}>
      {/* 筛选按钮 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="h-full px-4 flex items-center gap-2 hover:bg-gray-50 transition-colors text-sm font-medium text-gray-600 outline-none border-l border-gray-100"
      >
        <span className="text-xs text-gray-400">筛选</span>
        <ChevronUp
          size={14}
          className={`text-gray-400 transition-transform ${isOpen ? '' : 'rotate-180'}`}
        />
      </button>

      {/* 下拉面板 */}
      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-[340px] bg-white rounded-xl shadow-2xl border border-gray-200 z-30 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="px-4 py-3.5">
            <FilterSection
              title="排序依据"
              options={sortOptions}
              value={localFilters.sort_type}
              onChange={(value) => handleFilterChange('sort_type', value)}
            />

            <FilterSection
              title="发布时间"
              options={timeOptions}
              value={localFilters.publish_time}
              onChange={(value) => handleFilterChange('publish_time', value)}
            />

            <FilterSection
              title="视频时长"
              options={durationOptions}
              value={localFilters.filter_duration}
              onChange={(value) => handleFilterChange('filter_duration', value)}
            />

            <FilterSection
              title="搜索范围"
              options={rangeOptions}
              value={localFilters.search_range}
              onChange={(value) => handleFilterChange('search_range', value)}
            />
          </div>
        </div>
      )}
    </div>
  );
};
