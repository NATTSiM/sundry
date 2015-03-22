#!/usr/bin/perl

%JOBS = (
    -2 => "Total",
    -1 => "jtINVALID",
     0 => "jtPACK",
     1 => "jtPUBOLDLEDGER",
     2 => "jtVALIDATION",
     3 => "jtPROOFWORK",
     4 => "jtTRANSACTION_l",
     5 => "jtPROPOSAL_ut",
     6 => "jtLEDGER_DATA",
     7 => "jtCLIENT",
     8 => "jtRPC",
     9 => "jtUPDATE_PF",
    10 => "jtTRANSACTION",
    11 => "jtUNL",
    12 => "jtADVANCE",
    13 => "jtPUBLEDGER",
    14 => "jtTXN_DATA",
    15 => "jtWAL",
    16 => "jtVALIDATION_t",
    17 => "jtWRITE",
    18 => "jtACCEPT",
    19 => "jtPROPOSAL_T",
    20 => "jtSWEEP",
    21 => "jtNETOP_CLUSTER",
    22 => "jtNETOP_TIMER",
    23 => "jtADMIN",
    24 => "jtPEER",
    25 => "jtDISK",
    26 => "jtTXN_PROC",
    27 => "jtOB_SETUP",
    28 => "jtPATH_FIND",
    29 => "jtHO_READ",
    30 => "jtHO_WRITE",
    31 => "jtGENERIC",
    32 => "jtNS_SYNC_READ",
    33 => "jtNS_ASYNC_READ",
    34 => "jtNS_WRITE"
);

@previous = ();

print join("\t", "timestamp.usec", "job", "new", "completed", "waiting", "running") . "\n";
while(<STDIN>) {
    next unless /job queue counters: {(.*)} BM:(.*)/;
    my @counters = split(/;/, $1);
    (my $sec, my $usec) = split(/\./, $2);
    my $timestamp = localtime($sec);
    if (@previous) {
        for (my $i = 0; $i < $#counters; ++$i) {
            (my $type, my $vals) = split(/:/, $counters[$i]);
            (my $added, my $started, my $finished) = split(/,/, $vals);
            (my $type, my $prevvals) = split(/:/, $previous[$i]);
            (my $prevadded, my $prevstarted, my $prevfinished) = split(
                /,/, $prevvals);

            my $new = $added - $prevadded;
            my $waiting = $added - $started;
            my $running = $started - $finished;
            my $completed = $finished - $prevfinished;
            if ($new || $waiting || $running || $completed) {
                print join("\t", "$timestamp.$usec", $JOBS{$type}, $new, $completed, $waiting, $running)
                    . "\n";
            }
        }
    }

    @previous = @counters;
}

