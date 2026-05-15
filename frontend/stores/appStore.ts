import { create } from 'zustand';
import { DouyinWork, TaskType } from '../types';
import { FilterSettings } from '../components/SearchFilter';

interface AppState {
  activeTab: TaskType;
  inputVal: string;
  inputError: string | null;
  maxCount: number;
  isLoading: boolean;
  results: DouyinWork[];
  selectedWorkId: string | null;
  resultsTaskType: TaskType | null;
  savedInputVal: string;
  currentTaskId: string | null;
  isSettingsOpen: boolean;
  showLogs: boolean;
  showWelcomeWizard: boolean;
  filters: FilterSettings;

  setActiveTab: (tab: TaskType) => void;
  setInputVal: (val: string) => void;
  setInputError: (err: string | null) => void;
  setMaxCount: (count: number) => void;
  setIsLoading: (loading: boolean) => void;
  setResults: (results: DouyinWork[] | ((prev: DouyinWork[]) => DouyinWork[])) => void;
  setSelectedWorkId: (id: string | null) => void;
  setResultsTaskType: (type: TaskType | null) => void;
  setSavedInputVal: (val: string) => void;
  setCurrentTaskId: (id: string | null) => void;
  setIsSettingsOpen: (open: boolean) => void;
  setShowLogs: (show: boolean) => void;
  setShowWelcomeWizard: (show: boolean) => void;
  setFilters: (filters: FilterSettings | ((prev: FilterSettings) => FilterSettings)) => void;
  appendResults: (items: DouyinWork[]) => void;
  clearResults: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  activeTab: TaskType.POST,
  inputVal: '',
  inputError: null,
  maxCount: 0,
  isLoading: false,
  results: [],
  _resultIds: new Set<string>(),
  selectedWorkId: null,
  resultsTaskType: null,
  savedInputVal: '',
  currentTaskId: null,
  isSettingsOpen: false,
  showLogs: false,
  showWelcomeWizard: false,
  filters: {
    sort_type: '0',
    publish_time: '0',
    filter_duration: '',
    search_range: '0',
    content_type: '1',
  },

  setActiveTab: (tab) => set({ activeTab: tab }),
  setInputVal: (val) => set({ inputVal: val }),
  setInputError: (err) => set({ inputError: err }),
  setMaxCount: (count) => set({ maxCount: count }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setResults: (results) =>
    set((state) => ({
      results: typeof results === 'function' ? results(state.results) : results,
    })),
  setSelectedWorkId: (id) => set({ selectedWorkId: id }),
  setResultsTaskType: (type) => set({ resultsTaskType: type }),
  setSavedInputVal: (val) => set({ savedInputVal: val }),
  setCurrentTaskId: (id) => set({ currentTaskId: id }),
  setIsSettingsOpen: (open) => set({ isSettingsOpen: open }),
  setShowLogs: (show) => set({ showLogs: show }),
  setShowWelcomeWizard: (show) => set({ showWelcomeWizard: show }),
  setFilters: (filters) =>
    set((state) => ({
      filters: typeof filters === 'function' ? filters(state.filters) : filters,
    })),
  appendResults: (items) =>
    set((state) => {
      const existingIds = (state as any)._resultIds as Set<string>;
      const newItems = items.filter((item) => !existingIds.has(item.id));
      if (newItems.length === 0) return state;
      const updatedIds = new Set(existingIds);
      newItems.forEach((item) => updatedIds.add(item.id));
      return { results: [...state.results, ...newItems], _resultIds: updatedIds } as any;
    }),
  clearResults: () => set({ results: [], _resultIds: new Set<string>() } as any),
}));
