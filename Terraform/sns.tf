resource "aws_sns_topic" "anomaly_alerts" {
  name = "${var.project_name}-anomaly-alerts"

  tags = {
    Name = "${var.project_name}-anomaly-alerts"
  }
}

resource "aws_sns_topic_subscription" "email" {
  count     = length(var.alert_emails)
  topic_arn = aws_sns_topic.anomaly_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_emails[count.index]
}

# Alarma sobre la metrica custom AnomalySeverity que envia send_to_cloudwatch.py
# Dispara cuando la severidad media en 5 min es >= 2 (CPU >= 50% o anomalia con CPU alta)
resource "aws_cloudwatch_metric_alarm" "anomaly_severity" {
  alarm_name          = "${var.project_name}-anomaly-severity"
  alarm_description   = "Alerta cuando el modelo IA detecta severidad >= 2 en las EC2 Flask"
  namespace           = "Custom/AnomalyDetection"
  metric_name         = "AnomalySeverity"
  statistic           = "Maximum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 2
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.anomaly_alerts.arn]
  ok_actions    = [aws_sns_topic.anomaly_alerts.arn]

  tags = {
    Name = "${var.project_name}-anomaly-severity"
  }
}
