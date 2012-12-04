#!/usr/bin/perl

use IPC::Open3;
use IO::Handle;
use IO::Select; 

open(READ, "< $ARGV[0]") or die "READ Opemn fail"; 
open(WRITE, "> .$ARGV[0].tmp") or die "Write open fail"; 

my $pid = open3(\*CALC_IN, \*CALC_OUT, \*CALC_ERR, 'calc.py -t')
    or die "open3() failed $!";

READ->autoflush(1); 
WRITE->autoflush(1); 
CALC_IN->autoflush(1); 
CALC_OUT->autoflush(1); 
CALC_ERR->autoflush(1); 

my $s=IO::Select->new(); 
$s->add(\*CALC_OUT);
$s->add(\*CALC_ERR);

# fetch first ready 
my $ready=0; 
while ($ready==0){
	my @calc_fh=$s->can_read(2);
	foreach my $fh (@calc_fh) {
		$result=<$fh>;
		chomp($result);
		if ($result eq "ready") { $ready=1; } 
	}
}

while(<READ>) {
	if (/^%calc/) {
		print WRITE; 
		s/^%calc\ *//g;
		chomp;
		my $n="\n";
		if (/\r$/) { chop; $n="\r\n"; print "Dos Format detected\n";}
		$_=$_."\n";
		# calc that 
		print "Calculate $_"; 
		print CALC_IN;
		$ready=0;
		while ($ready==0){
			$ready=1;
			my @calc_fh=$s->can_read(3);
			foreach my $fh (@calc_fh) {
				$ready=0; 
				$result=<$fh>;
				chomp($result);
				if ($result eq "ready") { $ready=1; } else {
					if ($result) {
						print WRITE "%res ".$result.$n;
					}
				}
			}
		}
	} elsif (/^%res/) {
		# do nothing with result lines 
	} else { print WRITE; }
}

unlink($ARGV[0]) or die "TMP"; 
link(".$ARGV[0].tmp", $ARGV[0]) or die "TMP"; 
unlink(".$ARGV[0].tmp") or die "TMP"; 

