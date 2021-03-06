import { SearchListResult } from '../../components/SearchPage/types';

/* executeSearch */
export enum ExecuteSearch {
  ACTION = 'amundsen/search/EXECUTE_SEARCH',
  SUCCESS = 'amundsen/search/EXECUTE_SEARCH_SUCCESS',
  FAILURE = 'amundsen/search/EXECUTE_SEARCH_FAILURE',
}

export interface ExecuteSearchRequest {
  type: ExecuteSearch.ACTION;
  term: string;
  pageIndex: number;
}

interface ExecuteSearchResponse {
  type: ExecuteSearch.SUCCESS | ExecuteSearch.FAILURE;
  payload?: SearchReducerState;
}

export function executeSearch(term: string, pageIndex: number): ExecuteSearchRequest  {
  return {
    term,
    pageIndex,
    type: ExecuteSearch.ACTION,
  };
}
/* end executeSearch */

export type SearchReducerAction = ExecuteSearchRequest | ExecuteSearchResponse;

export interface SearchReducerState {
  pageIndex: number;
  searchResults: SearchListResult[];
  searchTerm: string;
  totalResults: number;
}

const initialState: SearchReducerState = {
  pageIndex: 0,
  searchResults: [],
  searchTerm: '',
  totalResults: 0,
};

export default function reducer(state: SearchReducerState = initialState, action: SearchReducerAction): SearchReducerState {
  switch (action.type) {
    case ExecuteSearch.SUCCESS:
      return action.payload;
    case ExecuteSearch.FAILURE:
      return initialState;
    default:
      return state;
  }
}
