#Create a simulator object
set ns [new Simulator]

# Define different colors for visualization in NAM
$ns color 1 Blue
$ns color 2 Red
$ns color 3 Yellow

# Open the NAM trace file
set namf [open out.nam w]
$ns namtrace-all $namf

# Open the trace files for different TCP connections
set f1 [open tcp1.tr w]
set f2 [open tcp2.tr w]

# Define a 'finish' procedure to handle the end of the simulation
proc finish {} {
    global ns namf f1 f2
    $ns flush-trace
    close $namf
    close $f1
    close $f2
    exec nam out.nam &
    exit 0
}

# Create eight nodes
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]
set n7 [$ns node]

# Create links between the nodes
$ns duplex-link $n0 $n1 10Mb 10ms DropTail
$ns duplex-link $n1 $n2 2.5Mb 40ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n2 $n4 2.5Mb 40ms DropTail
$ns duplex-link $n4 $n5 10Mb 10ms DropTail
$ns duplex-link $n4 $n6 2.5Mb 40ms DropTail
$ns duplex-link $n6 $n7 10Mb 10ms DropTail
$ns duplex-link $n1 $n6 2.5Mb 40ms DropTail

# Set the orientation for visualization
$ns duplex-link-op $n0 $n1 orient right
$ns duplex-link-op $n1 $n6 orient right
$ns duplex-link-op $n6 $n7 orient right
$ns duplex-link-op $n2 $n3 orient right
$ns duplex-link-op $n2 $n4 orient right
$ns duplex-link-op $n4 $n5 orient right

# Set Queue limit and Monitor the queue for the link between node 2 and node 4
$ns queue-limit $n2 $n4 10
$ns duplex-link-op $n2 $n4 queuePos 0.5

# Create a TCP agent and attach it to node n0
set tcp1 [new Agent/TCP]
$ns attach-agent $n0 $tcp1

# Sink for traffic at Node n5
set sink1 [new Agent/TCPSink]
$ns attach-agent $n5 $sink1

# Connect TCP1 and sink1
$ns connect $tcp1 $sink1
$tcp1 set fid_ 1

# Setup FTP over TCP connection for TCP1
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1

# Create a TCP agent and attach it to node n3
set tcp2 [new Agent/TCP]
$ns attach-agent $n3 $tcp2

# Sink for traffic at Node n5 (same as before)
$ns connect $tcp2 $sink1
$tcp2 set fid_ 2

# Setup FTP over TCP connection for TCP2
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2

# Create a TCP agent and attach it to node n7
set tcp3 [new Agent/TCP]
$ns attach-agent $n7 $tcp3

# Sink for traffic at Node n0
set sink2 [new Agent/TCPSink]
$ns attach-agent $n0 $sink2

# Connect TCP3 and sink2
$ns connect $tcp3 $sink2
$tcp3 set fid_ 3

# Setup FTP over TCP connection for TCP3
set ftp3 [new Application/FTP]
$ftp3 attach-agent $tcp3

# Sink for traffic at Node n3
set sink3 [new Agent/TCPSink]
$ns attach-agent $n3 $sink3

# Connect another TCP agent at n7 to n3
set tcp4 [new Agent/TCP]
$ns attach-agent $n7 $tcp4
$ns connect $tcp4 $sink3
$tcp4 set fid_ 4

# Setup FTP over TCP connection for TCP4
set ftp4 [new Application/FTP]
$ftp4 attach-agent $tcp4

proc record {} {
    global ns f1 f2 sink1 sink2
    set time 0.1
    set now [$ns now]
    set bw1 [$sink1 set bytes_]
    set bw2 [$sink2 set bytes_]
    puts $f1 "$now [expr $bw1/$time*8/1000000]"
    puts $f2 "$now [expr $bw2/$time*8/1000000]"
    $sink1 set bytes_ 0
    $sink2 set bytes_ 0
    $ns at [expr $now+$time] "record"
}

# Start recording throughput
$ns at 0.1 "record"

# Start the FTP sessions at scheduled times
$ns at 0.5 "$ftp1 start"
$ns at 2.0 "$ftp2 start"
$ns at 3.0 "$ftp3 start"
$ns at 4.0 "$ftp4 start"

# Stop FTP sessions
$ns at 8.5 "$ftp1 stop"
$ns at 9.5 "$ftp2 stop"
$ns at 9.5 "$ftp3 stop"
$ns at 7.0 "$ftp4 stop"

# Call the finish procedure after 10 seconds of simulation time
$ns at 10.0 "finish"

# Run the simulation
$ns run