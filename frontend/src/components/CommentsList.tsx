import React, { useState } from 'react';
import { MessageSquare, ThumbsUp } from 'lucide-react';
import type { CommentItem, SentimentCategory } from '../types';

interface CommentsListProps {
  comments: CommentItem[];
}

export const CommentsList: React.FC<CommentsListProps> = ({ comments }) => {
  const [filter, setFilter] = useState<'all' | SentimentCategory>('all');

  const filteredComments = comments.filter((c) => {
    if (filter === 'all') return true;
    return c.sentiment === filter;
  });

  if (comments.length === 0) {
    return null;
  }

  return (
    <div className="comments-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
        <h3 className="section-title" style={{ margin: 0 }}>
          <MessageSquare size={18} color="#06b6d4" />
          <span>Analyzed Comments Sample ({comments.length})</span>
        </h3>

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

      <div style={{ maxHeight: '480px', overflowY: 'auto', paddingRight: '4px' }}>
        {filteredComments.map((comment) => (
          <div key={comment.id} className="comment-card">
            <div className="comment-header">
              <span className="comment-author">{comment.author}</span>
              {comment.sentiment && (
                <span className={`comment-sentiment-badge ${comment.sentiment}`}>
                  {comment.sentiment} ({comment.sentiment_score !== undefined && comment.sentiment_score > 0 ? `+${comment.sentiment_score}` : comment.sentiment_score})
                </span>
              )}
            </div>

            <p className="comment-text">{comment.text}</p>

            <div className="comment-footer">
              {comment.likes !== undefined && comment.likes > 0 && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <ThumbsUp size={12} /> {comment.likes}
                </span>
              )}
              {comment.published_at && <span>{comment.published_at}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
