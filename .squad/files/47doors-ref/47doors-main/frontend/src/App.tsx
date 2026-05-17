import { useCallback, useState } from 'react';
import { ChatContainer } from './components/ChatContainer';
import { Header } from './components/Header';
import { TicketDashboard } from './components/TicketDashboard';
import { AdminDashboard } from './components/AdminDashboard';
import { RunbookPage } from './components/RunbookPage';
import { LivePage } from './components/LivePage';
import { useChat } from './hooks/useChat';
import { useTickets } from './hooks/useTickets';
import { useAdminTickets } from './hooks/useAdminTickets';
import { useHighContrast } from './hooks/useHighContrast';

type View = 'chat' | 'tickets' | 'admin' | 'runbook' | 'live';

/** Map URL pathname to initial view for direct-link support (/live, /runbook). */
function getInitialView(): View {
  const path = window.location.pathname.toLowerCase();
  if (path === '/live') return 'live';
  if (path === '/runbook') return 'runbook';
  return 'chat';
}

// Direct /live URL = audience mode: no header, no exit button
const isDirectLiveRoute = window.location.pathname.toLowerCase() === '/live';

function App() {
  const [highContrast, toggleHighContrast] = useHighContrast();
  const [currentView, setCurrentView] = useState<View>(getInitialView);

  const {
    messages,
    isLoading: chatLoading,
    sessionId,
    sendMessage,
    clearChat,
  } = useChat();

  const {
    tickets,
    selectedTicket,
    isLoading: ticketsLoading,
    error: ticketsError,
    refreshTickets,
    selectTicket,
    clearSelection,
  } = useTickets();

  const {
    tickets: adminTickets,
    selectedTicket: adminSelectedTicket,
    isLoading: adminLoading,
    error: adminError,
    statusFilter,
    departmentFilter,
    refreshTickets: adminRefreshTickets,
    selectTicket: adminSelectTicket,
    clearSelection: adminClearSelection,
    setStatusFilter,
    setDepartmentFilter,
    updateTicketStatus,
    deleteTicket,
  } = useAdminTickets();

  const handleTalkToHuman = useCallback(() => {
    sendMessage("I need to speak with a human support agent.");
    setCurrentView('chat');
  }, [sendMessage]);

  const handleViewChange = useCallback((view: View) => {
    setCurrentView(view);
    if (view === 'tickets') {
      refreshTickets();
    } else if (view === 'admin') {
      adminRefreshTickets();
    }
  }, [refreshTickets, adminRefreshTickets]);

  const getAriaLabel = () => {
    switch (currentView) {
      case 'chat':
        return 'Chat with support agent';
      case 'tickets':
        return 'Your support tickets';
      case 'admin':
        return 'Admin ticket management';
      case 'runbook':
        return 'Demo runbook and instructions';
      case 'live':
        return 'Live phone transcript for audience';
    }
  };

  return (
    <div className={`min-h-screen flex flex-col ${highContrast ? 'high-contrast' : ''}`}>
      {/* Skip link for accessibility */}
      <a
        href="#main-content"
        className="skip-link"
      >
        Skip to main content
      </a>

      {/* Hide header in Live view for clean full-screen projection */}
      {currentView !== 'live' && (
        <Header
          highContrast={highContrast}
          onToggleHighContrast={toggleHighContrast}
          onClearChat={clearChat}
          onTalkToHuman={handleTalkToHuman}
          currentView={currentView}
          onViewChange={handleViewChange}
        />
      )}

      {/* Live page is a full-screen overlay — render outside main container */}
      {currentView === 'live' && (
        <LivePage onExit={isDirectLiveRoute ? undefined : () => handleViewChange('runbook')} />
      )}

      {currentView !== 'live' && (
        <main
          id="main-content"
          className="flex-1 flex flex-col max-w-4xl w-full mx-auto"
          role="main"
          aria-label={getAriaLabel()}
        >
          {currentView === 'chat' && (
            <ChatContainer
              messages={messages}
              isLoading={chatLoading}
              sessionId={sessionId}
              onSendMessage={sendMessage}
            />
          )}
          {currentView === 'tickets' && (
            <TicketDashboard
              tickets={tickets}
              selectedTicket={selectedTicket}
              isLoading={ticketsLoading}
              error={ticketsError}
              onRefresh={refreshTickets}
              onSelectTicket={selectTicket}
              onClearSelection={clearSelection}
            />
          )}
          {currentView === 'admin' && (
            <AdminDashboard
              tickets={adminTickets}
              selectedTicket={adminSelectedTicket}
              isLoading={adminLoading}
              error={adminError}
              statusFilter={statusFilter}
              departmentFilter={departmentFilter}
              onRefresh={adminRefreshTickets}
              onSelectTicket={adminSelectTicket}
              onClearSelection={adminClearSelection}
              onSetStatusFilter={setStatusFilter}
              onSetDepartmentFilter={setDepartmentFilter}
              onUpdateStatus={updateTicketStatus}
              onDeleteTicket={deleteTicket}
            />
          )}
          {currentView === 'runbook' && <RunbookPage />}
        </main>
      )}
    </div>
  );
}

export default App;
