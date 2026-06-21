{{/*
Expand the name of the chart.
*/}}
{{- define "todo-backend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-backend.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end }}

{{/*
Create chart label value.
*/}}
{{- define "todo-backend.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Stable Kubernetes resource names.
*/}}
{{- define "todo-backend.deploymentName" -}}
{{- default "todo-app-backend" .Values.deployment.name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "todo-backend.serviceName" -}}
{{- default "todo-app-backend" .Values.service.name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "todo-backend.ingressName" -}}
{{- default (include "todo-backend.serviceName" .) .Values.ingress.name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "todo-backend.configName" -}}
{{- default (printf "%s-config" (include "todo-backend.fullname" .)) .Values.configMap.name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "todo-backend.secretName" -}}
{{- default (printf "%s-secret" (include "todo-backend.fullname" .)) .Values.secret.name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-backend.labels" -}}
helm.sh/chart: {{ include "todo-backend.chart" . }}
app.kubernetes.io/name: {{ include "todo-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app: todo-app-backend
{{- with .Values.labels }}
{{- toYaml . | nindent 0 }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: todo-app-backend
{{- end }}

{{/*
Namespace helper
*/}}
{{- define "todo-backend.namespace" -}}
{{- default .Release.Namespace .Values.namespace.name -}}
{{- end }}
