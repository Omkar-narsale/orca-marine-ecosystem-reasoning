/**
 * Map Controller for ORCA Marine Intelligence Platform
 * Provides unified programmatic control for Leaflet map operations, feature selection,
 * bounding box fitting, and conversational action query dispatching.
 */

import { MapActionCommand } from '@/types/marine';

export type MapEventHandler = (command: MapActionCommand) => void;

class MapControllerService {
  private listeners: Set<MapEventHandler> = new Set();
  private selectedFeatureId: string | null = null;
  private highlightedFeatureId: string | null = null;

  /**
   * Subscribe to map commands dispatched across the application
   */
  public subscribe(handler: MapEventHandler): () => void {
    this.listeners.add(handler);
    return () => {
      this.listeners.delete(handler);
    };
  }

  /**
   * Dispatch a MapActionCommand to all subscribed map instances
   */
  public dispatch(command: MapActionCommand): void {
    if (command.action === 'SELECT' && command.target_id) {
      this.selectedFeatureId = command.target_id;
    } else if (command.action === 'HIGHLIGHT' && command.target_id) {
      this.highlightedFeatureId = command.target_id;
    } else if (command.action === 'CLEAR') {
      this.selectedFeatureId = null;
      this.highlightedFeatureId = null;
    }

    this.listeners.forEach((listener) => {
      try {
        listener(command);
      } catch (err) {
        console.error('Error executing map action command listener:', err);
      }
    });
  }

  /**
   * Focus and select a specific feature on the map
   */
  public selectFeature(featureId: string, targetName?: string, center?: { lat: number; lng: number }): void {
    this.selectedFeatureId = featureId;
    this.dispatch({
      action: 'SELECT',
      target_id: featureId,
      target_name: targetName,
      center,
      zoom: 10
    });
  }

  /**
   * Highlight a feature (e.g. on hover or attention)
   */
  public highlightFeature(featureId: string): void {
    this.highlightedFeatureId = featureId;
    this.dispatch({
      action: 'HIGHLIGHT',
      target_id: featureId
    });
  }

  /**
   * Center the map on specific coordinates
   */
  public centerOnCoordinates(lat: number, lng: number, zoom: number = 9): void {
    this.dispatch({
      action: 'CENTER',
      center: { lat, lng },
      zoom
    });
  }

  /**
   * Fit map viewport to geographic bounding box
   */
  public fitBounds(geometryOrBounds: any): void {
    this.dispatch({
      action: 'FIT_BOUNDS',
      geometry: geometryOrBounds
    });
  }

  /**
   * Clear all selected/highlighted states
   */
  public clearSelection(): void {
    this.selectedFeatureId = null;
    this.highlightedFeatureId = null;
    this.dispatch({
      action: 'CLEAR'
    });
  }

  /**
   * Execute a batch of map action commands
   */
  public executeMapActions(actions: MapActionCommand[]): void {
    if (!actions || actions.length === 0) return;
    actions.forEach((cmd) => this.dispatch(cmd));
  }

  public getSelectedFeatureId(): string | null {
    return this.selectedFeatureId;
  }

  public getHighlightedFeatureId(): string | null {
    return this.highlightedFeatureId;
  }
}

export const mapController = new MapControllerService();
