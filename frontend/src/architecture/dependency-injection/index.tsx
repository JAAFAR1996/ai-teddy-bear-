import React, { createContext, useContext, ReactNode } from 'react';
import { Container } from './container';

interface DIContextType {
  container: Container;
}

const DIContext = createContext<DIContextType | undefined>(undefined);

interface DIProviderProps {
  container: Container;
  children: ReactNode;
}

export const DIProvider: React.FC<DIProviderProps> = ({ container, children }) => {
  return (
    <DIContext.Provider value={{ container }}>
      {children}
    </DIContext.Provider>
  );
};

export const useDI = (): Container => {
  const context = useContext(DIContext);
  if (!context) {
    throw new Error('useDI must be used within a DIProvider');
  }
  return context.container;
};

export const useService = <T,>(token: symbol | string): T => {
  const container = useDI();
  return container.resolve<T>(token);
}; 