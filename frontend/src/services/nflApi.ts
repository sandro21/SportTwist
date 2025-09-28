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
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.games || [];
    } catch (error) {
      console.error('Error fetching games:', error);
      return [];
    }
  }

  async searchGames(query: string): Promise<NFLGame[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.games || [];
    } catch (error) {
      console.error('Error searching games:', error);
      return [];
    }
  }

  // No JS fallbacks; rely on Python API

  async getPopularGames(): Promise<NFLGame[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/popular`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.games || [];
    } catch (error) {
      console.error('Error fetching popular games:', error);
      return [];
    }
  }

  async getGameDetails(gameId: string): Promise<any> {
    try {
      console.log(`Fetching game details for: ${gameId}`);
      const url = `${API_BASE_URL}/game/${gameId}`;
      console.log(`API URL: ${url}`);
      
      const response = await fetch(url);
      console.log(`Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API error response: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }
      
      const data = await response.json();
      console.log(`Received data keys: ${Object.keys(data)}`);
      
      return data;
    } catch (error) {
      console.error('Error fetching game details:', error);
      throw error; // Re-throw to let GamePage handle it
    }
  }

  async simulateGame(gameId: string, changeableAttributes: any, startPlayIndex: number): Promise<any> {
    try {
      console.log(`Simulating game ${gameId} from play ${startPlayIndex}:`, changeableAttributes);
      const url = `${API_BASE_URL}/simulate/`;
      
      const requestBody = {
        game_id: gameId,
        changeable_attributes: changeableAttributes,
        start_play_index: startPlayIndex
      };
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });
      
      console.log(`Simulation response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Simulation API error: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }
      
      const data = await response.json();
      console.log(`Simulation result:`, data);
      
      return data;
    } catch (error) {
      console.error('Error simulating game:', error);
      throw error;
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

  // No JS fallbacks; rely on Python API
}

export const nflApiService = new NFLApiService();