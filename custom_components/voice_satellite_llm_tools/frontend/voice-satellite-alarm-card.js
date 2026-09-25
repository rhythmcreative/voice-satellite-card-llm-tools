/**
 * Voice Satellite Alarm Card
 * Official Lovelace card for alarms matching the Voice Satellite design language.
 *
 * Implements 1:1 pixel-accurate layout for assets/alarm.png (hero)
 * and assets/alarm_list.png (list).
 */

(function () {
  'use strict';

  if (customElements.get('voice-satellite-alarm-card')) {
    return;
  }

  const ALARM_SVG = `
    <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
      <path d="M12,20A7,7 0 0,1 5,13A7,7 0 0,1 12,6A7,7 0 0,1 19,13A7,7 0 0,1 12,20M12,4A9,9 0 0,0 3,13A9,9 0 0,0 12,22A9,9 0 0,0 21,13A9,9 0 0,0 12,4M12.5,8H11V14L16.2,17.2L17,15.9L12.5,13.2V8M22,5.7L17.7,2.2L16.4,3.8L20.7,7.3L22,5.7M6.3,3.8L5,2.2L0.7,5.7L2,7.3L6.3,3.8Z"/>
    </svg>
  `;

  const SPEAKER_SVG = `
    <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
      <path d="M14,3.23V5.29C16.89,6.15 19,8.83 19,12C19,15.17 16.89,17.84 14,18.7V20.77C18,19.86 21,16.28 21,12C21,7.72 18,4.14 14,3.23M16.5,12C16.5,10.23 15.5,8.71 14,7.97V16C15.5,15.29 16.5,13.76 16.5,12M3,9V15H7L12,20V4L7,9H3Z"/>
    </svg>
  `;

  const WEEKDAY_NAMES_ES = [
    'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'
  ];
  const WEEKDAY_SHORT_ES = [
    'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'
  ];

  function formatDays(weekdays, repeat, short = false) {
    if (Array.isArray(weekdays) && weekdays.length > 0) {
      const sorted = [...weekdays].map(Number).sort((a, b) => a - b);
      if (sorted.length === 5 && sorted.every((d, i) => d === i)) {
        return short ? 'Lun-Vie' : 'Lunes a Viernes';
      }
      if (sorted.length === 2 && sorted[0] === 5 && sorted[1] === 6) {
        return short ? 'Sáb, Dom' : 'Fines de semana';
      }
      if (sorted.length === 7) {
        return short ? 'Diario' : 'Todos los días';
      }
      const list = short ? WEEKDAY_SHORT_ES : WEEKDAY_NAMES_ES;
      return sorted.map(d => list[d] || '').filter(Boolean).join(short ? ', ' : ' a ');
    }
    if (repeat === 'once' || repeat === 'never' || !repeat) {
      return 'Una vez';
    }
    if (repeat === 'weekly') {
      return 'Semanal';
    }
    return String(repeat);
  }

  function formatSpeaker(mediaPlayer) {
    if (!mediaPlayer) return '';
    return String(mediaPlayer)
      .replace('media_player.', '')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase())
      .trim();
  }

  const STYLES = `
    :host {
      display: block;
      width: 100%;
      font-family: 'Google Sans', Roboto, -apple-system, BlinkMacSystemFont, 'Segoe UI', Oxygen, Ubuntu, Cantarell, sans-serif;
      box-sizing: border-box;
      user-select: none;
      -webkit-user-select: none;
    }

    .alarm-card-container {
      background: #282a2d;
      border-radius: 28px;
      padding: 38px 42px 34px 42px;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.65), 0 2px 10px rgba(0, 0, 0, 0.3);
      color: #ffffff;
      box-sizing: border-box;
      width: 100%;
      max-width: 520px;
      margin: 0 auto;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    /* Single Hero Card (assets/alarm.png) */
    .hero-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 24px;
    }

    .hero-title-group {
      display: flex;
      align-items: center;
      gap: 14px;
      min-width: 0;
    }

    .hero-icon {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.08);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      color: #ffffff;
    }

    .hero-title {
      font-size: 24px;
      font-weight: 400;
      color: #ffffff;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      letter-spacing: -0.01em;
    }

    .hero-badge {
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.06em;
      padding: 6px 18px;
      border-radius: 20px;
      text-transform: uppercase;
      flex-shrink: 0;
    }

    .badge-scheduled, .badge-active, .badge-ringing {
      background: #c3e8cd;
      color: #137333;
    }

    .badge-reactivated, .badge-adjusted {
      background: #aecbfa;
      color: #041e49;
    }

    .badge-exists, .badge-snoozed {
      background: #fde293;
      color: #4a3800;
    }

    .badge-cancelled {
      background: #f6aea9;
      color: #4a0c08;
    }

    .badge-stopped, .badge-disabled {
      background: rgba(255, 255, 255, 0.12);
      color: #e3e3e3;
    }

    .hero-time {
      font-size: 96px;
      font-weight: 400;
      color: #f7f6f2;
      line-height: 1;
      margin: 36px 0 16px 0;
      text-align: center;
      letter-spacing: -2px;
      font-variant-numeric: tabular-nums;
      font-feature-settings: 'tnum' 1;
    }

    .hero-days {
      font-size: 24px;
      font-weight: 400;
      color: #e8eaed;
      text-align: center;
      margin-bottom: 12px;
      letter-spacing: -0.01em;
    }

    .hero-speaker {
      font-size: 19px;
      font-weight: 400;
      color: #dadce0;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-top: 4px;
    }

    /* List Card (assets/alarm_list.png) */
    .list-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .list-title-group {
      display: flex;
      align-items: center;
      gap: 14px;
      min-width: 0;
    }

    .list-title {
      font-size: 26px;
      font-weight: 500;
      color: #ffffff;
      letter-spacing: -0.01em;
    }

    .list-count-badge {
      font-size: 15px;
      font-weight: 600;
      color: #e3e3e3;
      background: rgba(255, 255, 255, 0.12);
      padding: 6px 18px;
      border-radius: 9999px;
      flex-shrink: 0;
    }

    .list-divider {
      height: 1px;
      background: rgba(255, 255, 255, 0.08);
      margin: 20px 0 10px 0;
    }

    .alarm-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 18px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    .alarm-row:last-child {
      border-bottom: none;
    }

    .row-time {
      font-size: 46px;
      font-weight: 400;
      color: #ffffff;
      min-width: 140px;
      letter-spacing: -0.5px;
      font-variant-numeric: tabular-nums;
      flex-shrink: 0;
    }

    .row-info {
      flex: 1;
      font-size: 22px;
      font-weight: 400;
      color: #e3e3e5;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      padding: 0 16px;
    }

    .row-badge {
      font-size: 14px;
      font-weight: 700;
      padding: 6px 18px;
      border-radius: 9999px;
      letter-spacing: 0.5px;
      flex-shrink: 0;
    }

    .row-badge.active {
      background: rgba(76, 175, 80, 0.18);
      color: #81c995;
    }

    .row-badge.off {
      background: rgba(255, 255, 255, 0.08);
      color: #9aa0a6;
    }

    .empty-state {
      text-align: center;
      padding: 20px 0;
    }

    .empty-icon {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.08);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
      color: #9aa0a6;
    }

    .empty-title {
      font-size: 24px;
      font-weight: 500;
      color: #ffffff;
      margin-bottom: 6px;
    }

    .empty-sub {
      font-size: 16px;
      color: #a8a8a8;
    }
  `;

  class VoiceSatelliteAlarmCard extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
      this._config = {};
      this._hass = null;
    }

    setConfig(config) {
      if (!config) {
        throw new Error('Invalid configuration');
      }
      this._config = { ...config };
      this._ensureFonts();
      this._render();
    }

    set hass(hass) {
      this._hass = hass;
      if (!this._config.alarm && !this._config.alarms) {
        this._render();
      }
    }

    getCardSize() {
      return this._config.mode === 'list' ? 4 : 3;
    }

    connectedCallback() {
      this._ensureFonts();
      this._render();
    }

    _ensureFonts() {
      if (!document.getElementById('vs-google-sans-font')) {
        const link = document.createElement('link');
        link.id = 'vs-google-sans-font';
        link.rel = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap';
        document.head.appendChild(link);
      }
    }

    _render() {
      if (!this.shadowRoot) return;

      const isList = this._config.mode === 'list' || (Array.isArray(this._config.alarms) && !this._config.alarm);
      const content = isList ? this._renderList() : this._renderHero();

      this.shadowRoot.innerHTML = `
        <style>${STYLES}</style>
        <div class="alarm-card-container">
          ${content}
        </div>
      `;
    }

    _renderHero() {
      let alarm = this._config.alarm;
      let action = this._config.action || 'scheduled';

      // Fallback: read from Home Assistant sensor if no explicit alarm object passed
      if (!alarm && this._hass) {
        const entId = this._config.entity || 'sensor.wakey_next_alarm';
        const stateObj = this._hass.states[entId];
        if (stateObj) {
          const attrs = stateObj.attributes || {};
          alarm = {
            time: attrs.time || stateObj.state,
            label: attrs.friendly_name || attrs.name || 'Alarma',
            days: attrs.days,
            weekdays: attrs.weekdays,
            repeat: attrs.repeat,
            media_player: attrs.media_player
          };
          if (stateObj.state === 'ringing') {
            action = 'ringing';
          }
        }
      }

      alarm = alarm || {};
      const timeStr = alarm.time || '--:--';
      const label = alarm.label || alarm.name || 'Alarma';
      const daysStr = alarm.days || formatDays(alarm.weekdays, alarm.repeat, false);
      const speaker = formatSpeaker(alarm.media_player);

      const statusMap = {
        scheduled: { cls: 'badge-scheduled', text: 'PROGRAMADA' },
        reactivated: { cls: 'badge-reactivated', text: 'REACTIVADA' },
        already_exists: { cls: 'badge-exists', text: 'YA EXISTE' },
        adjusted: { cls: 'badge-adjusted', text: 'AJUSTADA' },
        cancelled: { cls: 'badge-cancelled', text: 'CANCELADA' },
        snoozed: { cls: 'badge-snoozed', text: 'POSPUESTA' },
        stopped: { cls: 'badge-stopped', text: 'DETENIDA' },
        ringing: { cls: 'badge-ringing', text: 'SONANDO' },
        testing: { cls: 'badge-scheduled', text: 'PROGRAMADA' }
      };

      const status = statusMap[action] || statusMap.scheduled;
      const statusText = alarm.status_text || status.text;

      let speakerHtml = '';
      if (speaker) {
        speakerHtml = `
          <div class="hero-speaker">
            ${SPEAKER_SVG}
            <span>Altavoz: ${speaker}</span>
          </div>
        `;
      }

      return `
        <div class="hero-header">
          <div class="hero-title-group">
            <div class="hero-icon">
              ${ALARM_SVG}
            </div>
            <div class="hero-title">${label}</div>
          </div>
          <span class="hero-badge ${status.cls}">${statusText}</span>
        </div>
        <div class="hero-time">${timeStr}</div>
        <div class="hero-days">${daysStr}</div>
        ${speakerHtml}
      `;
    }

    _renderList() {
      const alarms = this._config.alarms || [];

      if (!alarms || alarms.length === 0) {
        return `
          <div class="empty-state">
            <div class="empty-icon">${ALARM_SVG}</div>
            <div class="empty-title">Sin alarmas programadas</div>
            <div class="empty-sub">Di "Pon una alarma a las 7:00" para crear una.</div>
          </div>
        `;
      }

      let activeCount = 0;
      const rowsHtml = alarms.map(a => {
        const time = a.time || '--:--';
        const name = a.name || a.label || 'Alarma';
        const enabled = a.enabled !== false;
        if (enabled) activeCount++;
        const days = a.days || formatDays(a.weekdays, a.repeat, true);

        const badgeHtml = enabled
          ? '<span class="row-badge active">ACTIVA</span>'
          : '<span class="row-badge off">OFF</span>';

        return `
          <div class="alarm-row">
            <span class="row-time">${time}</span>
            <span class="row-info">${name} • ${days}</span>
            ${badgeHtml}
          </div>
        `;
      }).join('');

      const countLabel = `${activeCount} activa${activeCount !== 1 ? 's' : ''}`;

      return `
        <div class="list-header">
          <div class="list-title-group">
            <div class="hero-icon">${ALARM_SVG}</div>
            <div class="list-title">Tus Alarmas</div>
          </div>
          <span class="list-count-badge">${countLabel}</span>
        </div>
        <div class="list-divider"></div>
        <div class="list-items">
          ${rowsHtml}
        </div>
      `;
    }
  }

  customElements.define('voice-satellite-alarm-card', VoiceSatelliteAlarmCard);

  // Register in Lovelace custom card picker
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: 'voice-satellite-alarm-card',
    name: 'Voice Satellite Alarm Card',
    description: 'Official alarm card matching the Voice Satellite card design language',
    preview: true,
    documentationURL: 'https://github.com/rhythmcreative/voice-satellite-card-llm-tools'
  });
})();
