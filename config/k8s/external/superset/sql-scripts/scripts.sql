-- get node metrics
SELECT DISTINCT metric FROM node_metrics

-- get node capacity
SELECT metric, AVG(value) as capacity FROM node_metrics
WHERE metric in ('capacity_cpu', 'capacity_hugepages_2Mi', 'capacity_hugepages_32Mi', 'capacity_hugepages_64Ki', 'capacity_pods', 'capacity_memory', 'capacity_hugepages_1Gi', 'capacity_cpu')
GROUP BY metric

-- get running containers details in node (line chart)
SELECT * FROM kubelet_metrics WHERE metric='kubelet_running_containers'

--- get running pods
SELECT * FROM kubelet_metrics WHERE metric='kubelet_running_pods'

-- get info about pods states in Node
SELECT metric, AVG(value) as number_of_pods
FROM kubelet_metrics
WHERE metric in ('kubelet_working_pods_desired_sync', 'kubelet_working_pods_desired_terminating', 'kubelet_working_pods_desired_terminated', 'kubelet_working_pods_orphan_sync', 'kubelet_working_pods_orphan_terminated', 'kubelet_working_pods_orphan_terminating')
GROUP BY metric

--- get phase for each pod
SELECT time, pod, phase FROM pod_phase WHERE status_flag=1 AND time=(
SELECT time as this_time FROM pod_phase ORDER BY time DESC LIMIT 1
)