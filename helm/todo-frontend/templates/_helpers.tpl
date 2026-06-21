{{/*
Expand the name of the chart.
*/}}
{{- define "todo-frontend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-frontend.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end }}

{{/*
Create chart label value.
*/}}
{{- define "todo-frontend.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Stable Kubernetes resource names.
*/}}
{{- define "todo-frontend.deploymentName" -}}
{{- default "todo-app-frontend" .Values.deployment.name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "todo-frontend.serviceName" -}}
{{- default "todo-app-frontend" .Values.service.name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "todo-frontend.ingressName" -}}
{{- default (include "todo-frontend.serviceName" .) .Values.ingress.name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "todo-frontend.appConfigName" -}}
{{- default (printf "%s-config" (include "todo-frontend.fullname" .)) .Values.configMap.name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "todo-frontend.secretName" -}}
{{- default (printf "%s-secret" (include "todo-frontend.fullname" .)) .Values.secret.name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "todo-frontend.nginxConfigName" -}}
{{- default "frontend-nginx-config" .Values.nginx.configMapName | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-frontend.labels" -}}
helm.sh/chart: {{ include "todo-frontend.chart" . }}
app.kubernetes.io/name: {{ include "todo-frontend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app: todo-app-frontend
{{- with .Values.labels }}
{{- toYaml . | nindent 0 }}
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
{{- default .Release.Namespace .Values.namespace.name -}}
{{- end }}
