"use client";

import React from "react";
import type { DoctorInfo } from "@/types/chat_schema";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MapPin, Clock, Stethoscope, Star } from "lucide-react";

interface DoctorCardProps {
  doctor: DoctorInfo;
  onSelect: (doctorName: string) => void;
}

export function DoctorCard({ doctor, onSelect }: DoctorCardProps) {
  return (
    <Card className="border-[var(--med-border)] bg-[var(--med-surface)] hover:shadow-lg transition-shadow duration-200">
      <CardContent className="p-4 space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <h3 className="font-heading font-semibold text-[var(--med-text-primary)] truncate">
              {doctor.full_name}
            </h3>
            {doctor.hospital_name && doctor.hospital_name !== doctor.full_name && (
              <p className="text-sm text-[var(--med-text-secondary)] truncate">
                {doctor.hospital_name}
              </p>
            )}
          </div>
          {/* Availability indicator */}
          {doctor.is_available !== undefined && doctor.is_available !== null && (
            <span
              className={`inline-block w-2.5 h-2.5 rounded-full mt-1.5 shrink-0 ${
                doctor.is_available
                  ? "bg-[var(--med-severity-low)]"
                  : "bg-[var(--med-text-muted)]"
              }`}
              title={doctor.is_available ? "Open Now" : "Hours N/A"}
            />
          )}
        </div>

        {/* Details */}
        <div className="space-y-1.5 text-sm text-[var(--med-text-secondary)]">
          <div className="flex items-center gap-2">
            <Stethoscope className="w-3.5 h-3.5 shrink-0" />
            <Badge variant="secondary" className="bg-[var(--med-surface-alt)] text-[var(--med-primary)] text-xs">
              {doctor.specialization}
            </Badge>
            {/* Rating */}
            {doctor.rating && (
              <span className="flex items-center gap-0.5 text-xs text-amber-600">
                <Star className="w-3 h-3 fill-amber-500 text-amber-500" />
                {doctor.rating}
                {doctor.user_ratings_total ? (
                  <span className="text-[var(--med-text-muted)]">
                    ({doctor.user_ratings_total})
                  </span>
                ) : null}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <MapPin className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">{doctor.clinic_address}</span>
          </div>
          {doctor.distance_km !== undefined && (
            <div className="flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 shrink-0" />
              <span>{doctor.distance_km} km away</span>
            </div>
          )}
        </div>

        {/* CTA */}
        <Button
          className="w-full bg-[var(--med-primary)] text-[var(--med-text-on-brand)] hover:bg-[var(--med-primary-light)] transition-colors"
          onClick={() => onSelect(doctor.full_name)}
        >
          Select Doctor
        </Button>
      </CardContent>
    </Card>
  );
}
