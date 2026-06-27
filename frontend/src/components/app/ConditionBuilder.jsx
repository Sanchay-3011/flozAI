import React, { useState, useCallback, useEffect } from 'react';
import {
  Filter,
  ChevronDown,
  CheckCircle2,
  AlertTriangle,
  X,
  Loader2,
  Sparkles,
  SlidersHorizontal,
  MessageSquare,
  Plus
} from 'lucide-react';
import { flozApi } from '../../services/api';
import styles from './ConditionBuilder.module.css';

/* ═══════════════════════════════════════════
   AVAILABLE FIELDS & OPERATORS
   ═══════════════════════════════════════════ */

const AVAILABLE_FIELDS = [
  { value: 'lead.status', label: 'Lead Status' },
  { value: 'amount', label: 'Amount' },
  { value: 'email', label: 'Email' },
  { value: 'name', label: 'Name' },
  { value: 'status', label: 'Status' },
  { value: 'score', label: 'Score' },
  { value: 'priority', label: 'Priority' },
  { value: 'source', label: 'Source' },
  { value: 'company', label: 'Company' },
  { value: 'country', label: 'Country' },
  { value: 'order.status', label: 'Order Status' },
  { value: 'order.total', label: 'Order Total' },
  { value: 'payment.status', label: 'Payment Status' },
  { value: 'deal.stage', label: 'Deal Stage' },
  { value: 'deal.value', label: 'Deal Value' },
  { value: 'customer.name', label: 'Customer Name' },
  { value: 'customer.email', label: 'Customer Email' },
];

const OPERATORS = [
  { value: 'equals', label: 'is', description: 'Equals' },
  { value: 'not_equals', label: 'is not', description: 'Not equals' },
  { value: 'contains', label: 'contains', description: 'Contains' },
  { value: 'greater_than', label: 'is greater than', description: 'Greater than (numbers)' },
  { value: 'exists', label: 'exists', description: 'Field exists' },
  { value: 'not_exists', label: 'does not exist', description: 'Field missing' },
];

const NO_VALUE_OPERATORS = ['exists', 'not_exists'];

function generateSummary(field, operator, value) {
  const fieldObj = AVAILABLE_FIELDS.find(f => f.value === field);
  const fieldLabel = fieldObj ? fieldObj.label : field?.replace(/\./g, ' ').replace(/\b\w/g, c => c.toUpperCase()) || 'Unknown';
  const opObj = OPERATORS.find(o => o.value === operator);
  const opLabel = opObj ? opObj.label : operator;
  if (NO_VALUE_OPERATORS.includes(operator)) {
    return `Only run if ${fieldLabel} ${opLabel}`;
  }
  return `Only run if ${fieldLabel} ${opLabel} ${value || '…'}`;
}

function makeEmptyCondition() {
  return { enabled: true, field: '', operator: 'equals', value: '', natural_language: '' };
}

/* ═══════════════════════════════════════════
   SINGLE CONDITION ROW
   ═══════════════════════════════════════════ */
function ConditionRow({ condition, index, total, onUpdate, onRemove }) {
  const [mode, setMode] = useState('builder');
  const [nlText, setNlText] = useState('');
  const [isParsing, setIsParsing] = useState(false);
  const [error, setError] = useState(null);

  const { field, operator, value } = condition;
  const hasValid = field && operator && (NO_VALUE_OPERATORS.includes(operator) || value);
  const summary = hasValid ? generateSummary(field, operator, value) : null;

  const update = (patch) => {
    const updated = { ...condition, ...patch };
    // Auto-generate natural language
    const f = patch.field ?? field;
    const o = patch.operator ?? operator;
    const v = patch.value ?? value;
    if (f && o && (NO_VALUE_OPERATORS.includes(o) || v)) {
      updated.natural_language = generateSummary(f, o, v);
    }
    onUpdate(index, updated);
  };

  const handleNLParse = async () => {
    if (!nlText.trim()) return;
    setIsParsing(true);
    setError(null);
    try {
      const data = await flozApi.parseCondition(nlText);
      if (data.needs_clarification) {
        setError({
          title: "We couldn't understand this condition",
          message: data.suggestion || "Try rephrasing. Example: 'Only if lead status is new'"
        });
      } else {
        const updated = {
          ...condition,
          field: data.field || '',
          operator: data.operator || 'equals',
          value: data.value || '',
          natural_language: data.natural_language || '',
        };
        onUpdate(index, updated);
        setError(null);
      }
    } catch (err) {
      setError({
        title: "Parsing failed",
        message: err.message || "Could not reach the condition parser. Make sure the backend is running."
      });
    } finally {
      setIsParsing(false);
    }
  };

  const handleNLKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleNLParse();
    }
  };

  return (
    <div className={styles.conditionRow}>
      {/* Row header */}
      <div className={styles.rowHeader}>
        <span className={styles.rowIndex}>
          {total > 1 ? `Condition ${index + 1}` : 'Condition'}
        </span>
        <button
          className={styles.rowRemove}
          onClick={() => onRemove(index)}
          title="Remove this condition"
        >
          <X size={12} />
        </button>
      </div>

      {/* Mode tabs */}
      <div className={styles.modeTabs}>
        <button
          className={`${styles.modeTab} ${mode === 'builder' ? styles.modeTabActive : ''}`}
          onClick={() => setMode('builder')}
        >
          <SlidersHorizontal size={12} /> Builder
        </button>
        <button
          className={`${styles.modeTab} ${mode === 'natural' ? styles.modeTabActive : ''}`}
          onClick={() => setMode('natural')}
        >
          <MessageSquare size={12} /> Describe
        </button>
      </div>

      {/* Builder Mode */}
      {mode === 'builder' && (
        <div className={styles.builderRow}>
          <div className={styles.builderField}>
            <span className={styles.builderLabel}>Run this step only if</span>
            <div className={styles.selectWrapper}>
              <select
                className={styles.select}
                value={field}
                onChange={(e) => { setError(null); update({ field: e.target.value }); }}
                id={`condition-field-${index}`}
              >
                <option value="">Select a field…</option>
                {AVAILABLE_FIELDS.map(f => (
                  <option key={f.value} value={f.value}>{f.label}</option>
                ))}
              </select>
              <ChevronDown size={14} className={styles.selectArrow} />
            </div>
          </div>
          <div className={styles.builderField}>
            <span className={styles.builderLabel}>Condition</span>
            <div className={styles.selectWrapper}>
              <select
                className={styles.select}
                value={operator}
                onChange={(e) => {
                  setError(null);
                  const v = e.target.value;
                  if (NO_VALUE_OPERATORS.includes(v)) {
                    update({ operator: v, value: '' });
                  } else {
                    update({ operator: v });
                  }
                }}
                id={`condition-operator-${index}`}
              >
                {OPERATORS.map(op => (
                  <option key={op.value} value={op.value}>{op.label}</option>
                ))}
              </select>
              <ChevronDown size={14} className={styles.selectArrow} />
            </div>
          </div>
          {!NO_VALUE_OPERATORS.includes(operator) && (
            <div className={styles.builderField}>
              <span className={styles.builderLabel}>Value</span>
              <input
                type="text"
                className={styles.valueInput}
                value={value}
                onChange={(e) => { setError(null); update({ value: e.target.value }); }}
                placeholder="Enter value…"
                id={`condition-value-${index}`}
              />
            </div>
          )}
        </div>
      )}

      {/* NL Mode */}
      {mode === 'natural' && (
        <div className={styles.nlInputWrapper}>
          <div className={styles.nlInputContainer}>
            <textarea
              className={styles.nlInput}
              value={nlText}
              onChange={(e) => setNlText(e.target.value)}
              onKeyDown={handleNLKeyDown}
              placeholder='e.g. "Only if the lead is new"'
              id={`condition-nl-${index}`}
            />
            <button
              className={styles.nlParseBtn}
              onClick={handleNLParse}
              disabled={isParsing || !nlText.trim()}
              title="Parse condition"
            >
              {isParsing ? <Loader2 size={14} /> : <Sparkles size={14} />}
            </button>
          </div>
          <span className={styles.nlHint}>
            Press Enter or click ✨ to parse. Describe the condition in plain English.
          </span>
        </div>
      )}

      {/* Parsing */}
      {isParsing && (
        <div className={styles.parsingState}>
          <Loader2 size={14} className={styles.parsingSpinner} />
          <span className={styles.parsingText}>Understanding your condition…</span>
        </div>
      )}

      {/* Error */}
      {error && !isParsing && (
        <div className={styles.errorPill}>
          <AlertTriangle size={14} className={styles.errorIcon} />
          <div className={styles.errorContent}>
            <span className={styles.errorTitle}>{error.title}</span>
            <span className={styles.errorMessage}>{error.message}</span>
          </div>
        </div>
      )}

      {/* Summary */}
      {hasValid && !error && !isParsing && (
        <div className={styles.summaryPill}>
          <CheckCircle2 size={14} className={styles.summaryIcon} />
          <span className={styles.summaryText}>{summary}</span>
        </div>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════
   CONDITION BUILDER — MULTI-CONDITION
   ═══════════════════════════════════════════ */
export default function ConditionBuilder({ conditions = [], onChange }) {
  const hasConditions = conditions.length > 0;
  const activeConditions = conditions.filter(c => c.enabled && c.field);

  const handleToggle = () => {
    if (hasConditions) {
      // Turn off — clear all conditions
      onChange([]);
    } else {
      // Turn on — add first condition
      onChange([makeEmptyCondition()]);
    }
  };

  const handleUpdateCondition = useCallback((index, updated) => {
    const next = [...conditions];
    next[index] = updated;
    onChange(next);
  }, [conditions, onChange]);

  const handleRemoveCondition = useCallback((index) => {
    const next = conditions.filter((_, i) => i !== index);
    onChange(next);
  }, [conditions, onChange]);

  const handleAddCondition = () => {
    onChange([...conditions, makeEmptyCondition()]);
  };

  return (
    <div className={`${styles.conditionCard} ${hasConditions ? styles.active : ''}`}>
      {/* Header with toggle */}
      <div className={styles.cardHeader}>
        <div className={styles.cardHeaderLeft}>
          <Filter size={14} className={styles.cardIcon} />
          <span>Conditions</span>
          {activeConditions.length > 0 && (
            <span className={styles.conditionCount}>{activeConditions.length}</span>
          )}
        </div>
        <div
          className={`${styles.toggle} ${hasConditions ? styles.toggleOn : ''}`}
          onClick={handleToggle}
          role="switch"
          aria-checked={hasConditions}
          tabIndex={0}
          title={hasConditions ? 'Remove all conditions' : 'Add a condition'}
        >
          <div className={styles.toggleKnob} />
        </div>
      </div>

      {/* Collapsed state */}
      {!hasConditions && (
        <div className={styles.collapsedInfo} onClick={handleToggle}>
          <Filter size={12} />
          <span>Add conditions to control when this step runs</span>
        </div>
      )}

      {/* Expanded body — all conditions */}
      {hasConditions && (
        <div className={styles.conditionBody}>
          {conditions.map((cond, i) => (
            <React.Fragment key={i}>
              {i > 0 && (
                <div className={styles.andDivider}>
                  <span className={styles.andLabel}>AND</span>
                </div>
              )}
              <ConditionRow
                condition={cond}
                index={i}
                total={conditions.length}
                onUpdate={handleUpdateCondition}
                onRemove={handleRemoveCondition}
              />
            </React.Fragment>
          ))}

          {/* Add another condition */}
          <button className={styles.addConditionBtn} onClick={handleAddCondition}>
            <Plus size={12} />
            <span>Add another condition</span>
          </button>

          {activeConditions.length > 1 && (
            <div className={styles.andNote}>
              All {activeConditions.length} conditions must be true for this step to run.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
