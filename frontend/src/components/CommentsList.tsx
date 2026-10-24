import React, { useState, useMemo } from 'react';
import { MessageSquare, ThumbsUp, Search, ArrowUpDown, X } from 'lucide-react';
import type { CommentItem, SentimentCategory } from '../types';

interface CommentsListProps {
  comments: CommentItem[];
  selectedKeyword?: string;
  onClearKeyword?: () => void;
}

type SortOption = 'default' | 'likes' | 'most-negative' | 'most-positive';

export const CommentsList: React.FC<CommentsListProps> = ({
  comments,
  selectedKeyword,
  onClearKeyword,
}) => {
  const [filter, setFilter] = useState<'all' | SentimentCategory>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortOption, setSortOption] = useState<SortOption>('default');

  const filteredAndSortedComments = useMemo(() => {
    return comments
      .filter((c) => {
        // Sentiment category filter
        if (filter !== 'all' && c.sentiment !== filter) return false;

        // Active driver keyword filter
        if (selectedKeyword) {
          const kw = selectedKeyword.toLowerCase();
          const textMatch = c.text?.toLowerCase().includes(kw);
          if (!textMatch) return false;
        }

        // Search query filter (matches comment text or author)
        if (searchQuery.trim()) {
          const query = searchQuery.toLowerCase().trim();
          const inText = c.text?.toLowerCase().includes(query);
          const inAuthor = c.author?.toLowerCase().includes(query);
          if (!inText && !inAuthor) return false;
        }

        return true;
      })
      .sort((a, b) => {
        if (sortOption === 'likes') {
          return (b.likes || 0) - (a.likes || 0);
        }
        if (sortOption === 'most-negative') {
          return (a.sentiment_score ?? 0) - (b.sentiment_score ?? 0);
        }
        if (sortOption === 'most-positive') {
          return (b.sentiment_score ?? 0) - (a.sentiment_score ?? 0);
        }
        return 0; // default order
      });
  }, [comments, filter, selectedKeyword, searchQuery, sortOption]);

  if (comments.length === 0) {
    return null;
  }

  return (
    <div className="comments-container">
      {/* Header & Main Controls */}
      <div className="comments-header-row">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <MessageSquare size={18} color="var(--accent-cyan)" />
          <h3 className="section-title" style={{ margin: 0 }}>
            Comment Explorer ({filteredAndSortedComments.length} of {comments.length})
          </h3>
        </div>

        {/* Filter Pills */}
        <div className="limit-pills">
          <button
            type="button"
            className={`limit-pill ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All ({comments.length})
          </button>
          <button
            type="button"
            className={`limit-pill ${filter === 'positive' ? 'active' : ''}`}
            onClick={() => setFilter('positive')}
          >
            Positive ({comments.filter((c) => c.sentiment === 'positive').length})
          </button>
          <button
            type="button"
            className={`limit-pill ${filter === 'neutral' ? 'active' : ''}`}
            onClick={() => setFilter('neutral')}
          >
            Neutral ({comments.filter((c) => c.sentiment === 'neutral').length})
          </button>
          <button
            type="button"
            className={`limit-pill ${filter === 'negative' ? 'active' : ''}`}
            onClick={() => setFilter('negative')}
          >
            Negative ({comments.filter((c) => c.sentiment === 'negative').length})
          </button>
        </div>
      </div>

      {/* Explorer Search & Sort Toolbar */}
      <div className="comments-toolbar">
        <div className="comment-search-box">
          <Search size={15} className="search-icon" />
          <input
            type="text"
            className="comment-search-input"
            placeholder="Search within comments or commenter names..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button
              type="button"
              className="clear-search-btn"
              onClick={() => setSearchQuery('')}
              title="Clear search"
            >
              <X size={14} />
            </button>
          )}
        </div>

        <div className="comment-sort-box">
          <ArrowUpDown size={14} className="sort-icon" />
          <select
            className="comment-sort-select"
            value={sortOption}
            onChange={(e) => setSortOption(e.target.value as SortOption)}
          >
            <option value="default">Sort: Default Order</option>
            <option value="likes">Sort: Most Liked (High Agreement)</option>
            <option value="most-negative">Sort: Most Critical (Negative First)</option>
            <option value="most-positive">Sort: Most Positive (Praise First)</option>
          </select>
        </div>
      </div>

      {/* Active Keyword Badge */}
      {selectedKeyword && (
        <div className="active-filter-badge-row">
          <span>Active Topic Filter: <strong>"{selectedKeyword}"</strong></span>
          <button
            type="button"
            className="clear-pill-btn"
            onClick={onClearKeyword}
            title="Remove topic filter"
          >
            <X size={12} />
          </button>
        </div>
      )}

      {/* Comment Cards List */}
      <div className="comments-scroll-area">
        {filteredAndSortedComments.length === 0 ? (
          <div className="no-comments-matched">
            No comments match your search/filter criteria.
          </div>
        ) : (
          filteredAndSortedComments.map((comment) => (
            <div key={comment.id} className="comment-card">
              <div className="comment-header">
                <span className="comment-author">{comment.author}</span>
                {comment.sentiment && (
                  <span className={`comment-sentiment-badge ${comment.sentiment}`}>
                    {comment.sentiment}{' '}
                    {comment.sentiment_score !== undefined
                      ? `(${comment.sentiment_score > 0 ? `+${comment.sentiment_score}` : comment.sentiment_score})`
                      : ''}
                  </span>
                )}
              </div>

              <p className="comment-text">{comment.text}</p>

              <div className="comment-footer">
                {comment.likes !== undefined && comment.likes > 0 && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <ThumbsUp size={12} /> {comment.likes.toLocaleString()}
                  </span>
                )}
                {comment.published_at && <span>{comment.published_at}</span>}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

