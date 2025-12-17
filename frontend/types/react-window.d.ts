/**
 * react-window 类型声明
 * 解决 react-window 库类型定义不完整的问题
 */

declare module 'react-window' {
  import * as React from 'react';

  export interface ListChildComponentProps<T = any> {
    index: number;
    style: React.CSSProperties;
    data: T;
  }

  export interface FixedSizeListProps<T = any> {
    children: React.ComponentType<ListChildComponentProps<T>>;
    height: number;
    width: number;
    itemCount: number;
    itemSize: number;
    itemData?: T;
    overscanCount?: number;
    onItemsRendered?: (props: {
      overscanStartIndex: number;
      overscanStopIndex: number;
      visibleStartIndex: number;
      visibleStopIndex: number;
    }) => void;
    onScroll?: (props: {
      scrollDirection: 'forward' | 'backward';
      scrollOffset: number;
      scrollUpdateWasRequested: boolean;
    }) => void;
    initialScrollOffset?: number;
    useIsScrolling?: boolean;
    className?: string;
    style?: React.CSSProperties;
  }

  export class FixedSizeList<T = any> extends React.Component<FixedSizeListProps<T>> {
    scrollTo(scrollOffset: number): void;
    scrollToItem(index: number, align?: 'auto' | 'smart' | 'center' | 'end' | 'start'): void;
  }

  export interface VariableSizeListProps<T = any> {
    children: React.ComponentType<ListChildComponentProps<T>>;
    height: number;
    width: number;
    itemCount: number;
    itemSize: (index: number) => number;
    itemData?: T;
    overscanCount?: number;
    estimatedItemSize?: number;
  }

  export class VariableSizeList<T = any> extends React.Component<VariableSizeListProps<T>> {
    scrollTo(scrollOffset: number): void;
    scrollToItem(index: number, align?: 'auto' | 'smart' | 'center' | 'end' | 'start'): void;
    resetAfterIndex(index: number, shouldForceUpdate?: boolean): void;
  }
}
