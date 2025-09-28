// API service for communicating with the NFL backend
const API_BASE_URL = 'http://localhost:5001/api';

export interface NFLGame {
  game_id: string;
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  week: number;
  season: number;
  gameday: string;
  gametime: string;
}

export interface GameDetails extends NFLGame {
  total_plays: number;
}

class NFLApiService {
  async fetchGames(): Promise<NFLGame[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/games`);
      if (!response.ok) {
        if (response.status === 500) {
          console.warn('Backend is still loading NFL data, using fallback data');
          return this.getFallbackGames();
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.games || [];
    } catch (error) {
      console.error('Error fetching games:', error);
      console.warn('Using fallback data');
      return this.getFallbackGames();
    }
  }

  async searchGames(query: string): Promise<NFLGame[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) {
        if (response.status === 500) {
          console.warn('Backend is still loading NFL data, using fallback search');
          return this.searchFallbackGames(query);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.games || [];
    } catch (error) {
      console.error('Error searching games:', error);
      console.warn('Using fallback search');
      return this.searchFallbackGames(query);
    }
  }

  // Enhanced search for fallback data including team name matching
  private searchFallbackGames(query: string): NFLGame[] {
    const searchTerm = query.toLowerCase();
    const fallbackGames = this.getFallbackGames();
    
    // Team name mappings for better search
    const teamNameMap: Record<string, string> = {
      'eagles': 'PHI', 'philadelphia': 'PHI',
      'cowboys': 'DAL', 'dallas': 'DAL',
      'chiefs': 'KC', 'kansas': 'KC',
      'bills': 'BUF', 'buffalo': 'BUF',
      'packers': 'GB', 'green bay': 'GB',
      'vikings': 'MIN', 'minnesota': 'MIN',
      'patriots': 'NE', 'new england': 'NE',
      'dolphins': 'MIA', 'miami': 'MIA',
      'steelers': 'PIT', 'pittsburgh': 'PIT',
      'ravens': 'BAL', 'baltimore': 'BAL',
      '49ers': 'SF', 'niners': 'SF', 'san francisco': 'SF',
      'seahawks': 'SEA', 'seattle': 'SEA'
    };
    
    return fallbackGames.filter(game => {
      // Check team abbreviations
      const teamMatch = game.home_team.toLowerCase().includes(searchTerm) || 
                       game.away_team.toLowerCase().includes(searchTerm);
      
      // Check team names
      const teamNameMatch = Object.entries(teamNameMap).some(([name, abbrev]) => 
        searchTerm.includes(name) && (game.home_team === abbrev || game.away_team === abbrev)
      );
      
      // Check week
      const weekMatch = searchTerm.includes('week') && searchTerm.includes(game.week.toString());
      
      // Check season
      const seasonMatch = searchTerm.includes(game.season.toString());
      
      return teamMatch || teamNameMatch || weekMatch || seasonMatch;
    });
  }

  async getPopularGames(): Promise<NFLGame[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/popular`);
      if (!response.ok) {
        if (response.status === 500) {
          console.warn('Backend is still loading NFL data, using fallback data');
          return this.getFallbackGames();
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.games || [];
    } catch (error) {
      console.error('Error fetching popular games:', error);
      console.warn('Using fallback data');
      return this.getFallbackGames();
    }
  }

  async getGameDetails(gameId: string): Promise<GameDetails | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/game/${gameId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching game details:', error);
      return null;
    }
  }

  // Helper function to format team names for display
  formatTeamsString(game: NFLGame): string {
    return `${game.away_team} vs ${game.home_team}`;
  }

  // Helper function to format game date
  formatGameDate(game: NFLGame): string {
    const date = new Date(game.gameday);
    const options: Intl.DateTimeFormatOptions = { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    };
    return `${date.toLocaleDateString('en-US', options)}  •  Week ${game.week}`;
  }

  // Helper function to get winner
  getWinner(game: NFLGame): 'home' | 'away' | 'tie' {
    if (game.home_score > game.away_score) return 'home';
    if (game.away_score > game.home_score) return 'away';
    return 'tie';
  }

  // Fallback data when backend is not ready
  private getFallbackGames(): NFLGame[] {
    return [
      {
        game_id: '2024_03_PHI_DAL',
        home_team: 'DAL',
        away_team: 'PHI',
        home_score: 24,
        away_score: 28,
        week: 3,
        season: 2024,
        gameday: '2024-09-15',
        gametime: '20:30:00'
      },
      {
        game_id: '2024_05_KC_BUF',
        home_team: 'BUF',
        away_team: 'KC',
        home_score: 21,
        away_score: 31,
        week: 5,
        season: 2024,
        gameday: '2024-09-29',
        gametime: '20:30:00'
      },
      {
        game_id: '2024_06_GB_MIN',
        home_team: 'MIN',
        away_team: 'GB',
        home_score: 17,
        away_score: 24,
        week: 6,
        season: 2024,
        gameday: '2024-10-06',
        gametime: '13:00:00'
      },
      {
        game_id: '2024_07_NE_MIA',
        home_team: 'MIA',
        away_team: 'NE',
        home_score: 14,
        away_score: 10,
        week: 7,
        season: 2024,
        gameday: '2024-10-13',
        gametime: '13:00:00'
      },
      {
        game_id: '2024_08_PIT_BAL',
        home_team: 'BAL',
        away_team: 'PIT',
        home_score: 27,
        away_score: 24,
        week: 8,
        season: 2024,
        gameday: '2024-10-20',
        gametime: '20:30:00'
      },
      {
        game_id: '2024_09_SF_SEA',
        home_team: 'SEA',
        away_team: 'SF',
        home_score: 20,
        away_score: 35,
        week: 9,
        season: 2024,
        gameday: '2024-10-27',
        gametime: '16:25:00'
      }
    ];
  }
}

export const nflApiService = new NFLApiService();