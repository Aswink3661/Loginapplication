{{/*
Expand the name of the chart.
*/}}
{{- define "todo-frontend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-frontend.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-frontend.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "todo-frontend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app: todo-app-frontend
{{- with .Values.labels }}
project: {{ .project }}
environment: {{ .environment }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-frontend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: todo-app-frontend
{{- end }}

{{/*
Namespace helper
*/}}
{{- define "todo-frontend.namespace" -}}
{{- .Values.namespace.name }}
{{- end }}
