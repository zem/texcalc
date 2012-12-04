#!/usr/bin/perl

use IPC::Open3;
use IO::Handle;
use IO::Select; 

my $leavetexfile; 
my $pdflatex; 
my $texfile; 
while (my $arg=shift(@ARGV)) {
	if ($arg eq "-c") {
		# -compile
		$pdflatex="pdflatex"; 
	} elsif ($arg eq "-C") {
		if (shift(@ARGV) eq "-y") {
			# -compile
			$pdflatex="pdflatex"; 
			$leavetexfile=1;
		} else { 
			die "-C must be followed by -y\n"; 
		}
	} else { 
		$texfile=$arg;
	}
}

open(READ, "< $texfile") or die "READ Opemn fail"; 
open(WRITE, "> .$texfile.tmp") or die "Write open fail"; 

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

sub calculate {
	my $cmd=shift; 
	print "Calculate $cmd\n"; 
	my @ret; 
	print CALC_IN $cmd."\n"; 
	my $ready=0; 
	while ($ready==0){
		$ready=1;
		my @calc_fh=$s->can_read(3);
		foreach my $fh (@calc_fh) {
			$ready=0; 
			$result=<$fh>;
			chomp($result);
			if ($result eq "ready") { 
				$ready=1; 
			} else {
				if ($result) {
					push @ret, $result; 
				}
			}
		}
	}
	return @ret; 
}

sub insert_pyvar {
	my $var=shift; 
	print "Insertin Variable $var\n"; 
	my @ret=calculate("uround($var)"); 
	$ret[0]=~s/^\s+//g; 
	$ret[0]=~s/\s+$//g; 
	my ($val, $uncert)=split(/\+\/\-/, $ret[0]); 
	if ($uncert) {
		return "($val \\pm $uncert)"; 
	} else {
		return $val;
	}
}

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
		#$_=$_."\n";
		# calc that 
		foreach my $result (calculate($_)) {
			print WRITE "%res ".$result.$n; 
		}
	} elsif (/^%res/) {
		# do nothing with result lines 
	} else { print WRITE; }
}

close READ; 
close WRITE; 

unlink($texfile) or die "TMP"; 
if (!$pdflatex) {
	link(".$texfile.tmp", $texfile) or die "TMP"; 
	unlink(".$texfile.tmp") or die "TMP"; 
} else {
	open(READ, "< .$texfile.tmp") or die "Write open fail"; 
	open(WRITE, "> $texfile") or die "READ Opemn fail"; 
	READ->autoflush(1); 
	WRITE->autoflush(1); 

	while(<READ>){
		s/\@((\w|\d)+)\@/insert_pyvar($1)/gex; 
		print WRITE; 
	}

	close READ; 
	close WRITE; 

	system("$pdflatex $texfile") or print "calling pdflatex failed\n"; 
	system("$pdflatex $texfile") or print "calling pdflatex failed\n"; 
	
	if ( ! $leavetexfile) {
		unlink($texfile) or die "TMP"; 
		link(".$texfile.tmp", $texfile) or die "TMP"; 
	}
	unlink(".$texfile.tmp") or die "TMP"; 
}

