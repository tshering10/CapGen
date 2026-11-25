"use client";

import {
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
  type RefObject,
  useEffect,
  useRef,
  useState,
} from "react";
import type { SubtitleSegment, SubtitleStyle } from "@/types/subtitles";

interface VideoPreviewProps {
  src: string;
  segments: SubtitleSegment[];
  style?: SubtitleStyle;
  selectedSegmentId?: string | null;
  onStyleChange?: (style: SubtitleStyle) => void;
  onPositionCommit?: (style: SubtitleStyle) => void;
  onSelectSegment?: (segmentId: string | null) => void;
  onActiveChange?: (segment: SubtitleSegment | null) => void;
  videoRef?: RefObject<HTMLVideoElement | null>;
}

interface DragSession {
  pointerId: number;
  pointerOffsetX: number;
  pointerOffsetY: number;
}

interface AlignmentGuides {
  centerX: boolean;
  centerY: boolean;
  left: boolean;
  right: boolean;
  top: boolean;
  bottom: boolean;
}

const EMPTY_GUIDES: AlignmentGuides = {
  centerX: false,
  centerY: false,
  left: false,
  right: false,
  top: false,
  bottom: false,
};

const DEFAULT_STYLE: SubtitleStyle = {
  preset: "classic",
  font_family: "Arial",
  font_size: 32,
  font_color: "#FFFFFF",
  background_color: "#000000",
  background_opacity: 0.75,
  alignment: "center",
  position_x: 0.5,
  position_y: 0.85,
};

const SNAP_DISTANCE = 9;

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function backgroundColor(hex: string, opacity: number): string {
  const value = hex.replace("#", "");
  if (!/^[\da-f]{6}$/i.test(value)) {
    return `rgba(0, 0, 0, ${opacity})`;
  }
  const red = parseInt(value.slice(0, 2), 16);
  const green = parseInt(value.slice(2, 4), 16);
  const blue = parseInt(value.slice(4, 6), 16);
  return `rgba(${red}, ${green}, ${blue}, ${opacity})`;
}

export default function VideoPreview({
  src,
  segments,
  style,
  selectedSegmentId = null,
  onStyleChange,
  onPositionCommit,
  onSelectSegment,
  onActiveChange,
  videoRef,
}: VideoPreviewProps) {
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const frameRef = useRef<HTMLDivElement>(null);
  const layerRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef<DragSession | null>(null);
  const latestStyleRef = useRef(style ?? DEFAULT_STYLE);
  const [playbackSegment, setPlaybackSegment] = useState<SubtitleSegment | null>(
    null,
  );
  const [dragging, setDragging] = useState(false);
  const [guides, setGuides] = useState(EMPTY_GUIDES);
  const [frameWidth, setFrameWidth] = useState(0);
  const activeStyle = style ?? DEFAULT_STYLE;

  const currentVideoRef = videoRef ?? localVideoRef;
  const selectedSegment = segments.find(
    (segment) => segment.id === selectedSegmentId,
  );
  const visibleSegment = selectedSegment ?? playbackSegment;
  const isSelected = Boolean(selectedSegment);

  useEffect(() => {
    latestStyleRef.current = activeStyle;
  }, [activeStyle]);

  useEffect(() => {
    const frame = frameRef.current;
    if (!frame) return;

    const observer = new ResizeObserver(([entry]) => {
      setFrameWidth(entry.contentRect.width);
    });
    observer.observe(frame);
    return () => observer.disconnect();
  }, [src]);

  useEffect(() => {
    const video = currentVideoRef.current;
    if (!video) return;

    const updateActiveSegment = () => {
      const current = video.currentTime;
      const active =
        segments.find(
          (segment) => current >= segment.start && current <= segment.end,
        ) ?? null;
      setPlaybackSegment(active);
      onActiveChange?.(active);
    };

    video.addEventListener("timeupdate", updateActiveSegment);
    updateActiveSegment();
    return () => video.removeEventListener("timeupdate", updateActiveSegment);
  }, [currentVideoRef, onActiveChange, segments]);

  function handleFramePointerDown(event: ReactPointerEvent<HTMLDivElement>) {
    const target = event.target;
    if (
      target instanceof Element &&
      target.closest("[data-subtitle-layer]")
    ) {
      return;
    }
    onSelectSegment?.(null);
  }

  function handleLayerPointerDown(event: ReactPointerEvent<HTMLDivElement>) {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    const frame = frameRef.current;
    const layer = layerRef.current;
    if (!frame || !layer) return;

    event.preventDefault();
    onSelectSegment?.(visibleSegment?.id ?? null);
    event.currentTarget.setPointerCapture(event.pointerId);
    const layerBounds = layer.getBoundingClientRect();
    dragRef.current = {
      pointerId: event.pointerId,
      pointerOffsetX: event.clientX - layerBounds.left,
      pointerOffsetY: event.clientY - layerBounds.top,
    };
    setDragging(true);
  }

  function handleLayerPointerMove(event: ReactPointerEvent<HTMLDivElement>) {
    const drag = dragRef.current;
    const frame = frameRef.current;
    const layer = layerRef.current;
    if (!drag || drag.pointerId !== event.pointerId || !frame || !layer) return;

    event.preventDefault();
    const frameBounds = frame.getBoundingClientRect();
    const layerBounds = layer.getBoundingClientRect();
    const frameWidth = frameBounds.width;
    const frameHeight = frameBounds.height;
    if (!frameWidth || !frameHeight) return;

    const alignment = latestStyleRef.current.alignment;
    const anchorFactor = alignment === "left" ? 0 : alignment === "right" ? 1 : 0.5;
    const widthRatio = Math.min(layerBounds.width / frameWidth, 0.9);
    const heightRatio = Math.min(layerBounds.height / frameHeight, 1);
    const minX = anchorFactor * widthRatio;
    const maxX = 1 - (1 - anchorFactor) * widthRatio;
    const minY = 0;
    const maxY = Math.max(0, 1 - heightRatio);

    const targetLeft = event.clientX - drag.pointerOffsetX;
    const targetTop = event.clientY - drag.pointerOffsetY;
    let x = (targetLeft - frameBounds.left) / frameWidth + anchorFactor * widthRatio;
    let y = (targetTop - frameBounds.top) / frameHeight;
    x = clamp(x, minX, maxX);
    y = clamp(y, minY, maxY);

    const centerOffsetX = (0.5 - anchorFactor) * widthRatio;
    const centerX = x + centerOffsetX;
    const centerY = y + heightRatio / 2;
    const snapX = Math.abs(centerX - 0.5) * frameWidth <= SNAP_DISTANCE;
    const snapY = Math.abs(centerY - 0.5) * frameHeight <= SNAP_DISTANCE;
    if (snapX) x = clamp(0.5 - centerOffsetX, minX, maxX);
    if (snapY) y = clamp(0.5 - heightRatio / 2, minY, maxY);

    const layerLeft = x * frameWidth - anchorFactor * layerBounds.width;
    const layerTop = y * frameHeight;
    const left = layerLeft <= SNAP_DISTANCE;
    const right = frameWidth - (layerLeft + layerBounds.width) <= SNAP_DISTANCE;
    const top = layerTop <= SNAP_DISTANCE;
    const bottom = frameHeight - (layerTop + layerBounds.height) <= SNAP_DISTANCE;

    const nextStyle = {
      ...latestStyleRef.current,
      position_x: x,
      position_y: y,
    };
    latestStyleRef.current = nextStyle;
    setGuides({ centerX: snapX, centerY: snapY, left, right, top, bottom });
    onStyleChange?.(nextStyle);
  }

  function endDrag(event: ReactPointerEvent<HTMLDivElement>) {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) return;
    dragRef.current = null;
    setDragging(false);
    setGuides(EMPTY_GUIDES);
    onPositionCommit?.(latestStyleRef.current);
  }

  const anchorTransform =
    activeStyle.alignment === "left"
      ? "0%"
      : activeStyle.alignment === "right"
        ? "-100%"
        : "-50%";

  const layerStyle: CSSProperties = {
    left: `${activeStyle.position_x * 100}%`,
    top: `${activeStyle.position_y * 100}%`,
    transform: `translateX(${anchorTransform})`,
    color: activeStyle.font_color,
    backgroundColor: backgroundColor(
      activeStyle.background_color,
      activeStyle.background_opacity,
    ),
    fontFamily: activeStyle.font_family,
    fontSize: `${Math.max(10, activeStyle.font_size * (frameWidth / 1080))}px`,
    textAlign: activeStyle.alignment,
  };

  return (
    <div
      ref={frameRef}
      className="relative w-full overflow-hidden bg-black"
      onPointerDown={handleFramePointerDown}
    >
      <video
        ref={currentVideoRef}
        src={src}
        controls
        className="block h-auto w-full"
      />

      {dragging && (
        <div className="pointer-events-none absolute inset-0 z-10" aria-hidden="true">
          {guides.centerX && (
            <span className="absolute bottom-0 left-1/2 top-0 w-px -translate-x-1/2 bg-[#06B6D4]" />
          )}
          {guides.centerY && (
            <span className="absolute left-0 right-0 top-1/2 h-px -translate-y-1/2 bg-[#06B6D4]" />
          )}
          {guides.left && <span className="absolute bottom-0 left-0 top-0 w-px bg-[#6366F1]" />}
          {guides.right && <span className="absolute bottom-0 right-0 top-0 w-px bg-[#6366F1]" />}
          {guides.top && <span className="absolute left-0 right-0 top-0 h-px bg-[#6366F1]" />}
          {guides.bottom && <span className="absolute bottom-0 left-0 right-0 h-px bg-[#6366F1]" />}
        </div>
      )}

      {visibleSegment && (
        <div
          ref={layerRef}
          data-subtitle-layer
          className={`absolute z-20 max-w-[90%] whitespace-pre-wrap rounded-sm px-2 py-1 ${
            isSelected
              ? "cursor-grab active:cursor-grabbing border border-[#06B6D4] outline outline-1 outline-[#6366D4]/60"
              : "pointer-events-none border border-transparent"
          } ${dragging ? "select-none" : ""}`}
          style={{
            ...layerStyle,
            touchAction: "none",
            userSelect: "none",
            WebkitUserSelect: "none",
          }}
          onPointerDown={isSelected ? handleLayerPointerDown : undefined}
          onPointerMove={isSelected ? handleLayerPointerMove : undefined}
          onPointerUp={isSelected ? endDrag : undefined}
          onPointerCancel={isSelected ? endDrag : undefined}
          onLostPointerCapture={isSelected ? endDrag : undefined}
        >
          {visibleSegment.text}
          {isSelected && (
            <>
              <span className="pointer-events-none absolute -left-1 -top-1 h-2 w-2 border-l-2 border-t-2 border-[#6366D4]" />
              <span className="pointer-events-none absolute -right-1 -top-1 h-2 w-2 border-r-2 border-t-2 border-[#6366D4]" />
              <span className="pointer-events-none absolute -bottom-1 -left-1 h-2 w-2 border-b-2 border-l-2 border-[#6366D4]" />
              <span className="pointer-events-none absolute -bottom-1 -right-1 h-2 w-2 border-b-2 border-r-2 border-[#6366D4]" />
            </>
          )}
        </div>
      )}
    </div>
  );
}
