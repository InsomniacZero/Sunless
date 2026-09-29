declare module "react" {
  export const useState: any;
  export const useEffect: any;
  export interface FC<P = {}> {
    (props: P, context?: any): any;
  }
  const React: any;
  export default React;
}

declare module "framer-motion" {
  export const motion: any;
  export const AnimatePresence: any;
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}
