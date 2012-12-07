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
open(WRITE2, "> .$texfile.tmp2") or die "Write open fail"; 

my $pid = open3(\*CALC_IN, \*CALC_OUT, \*CALC_ERR, 'calc.py -t')
    or die "open3() failed $!";

READ->autoflush(1); 
WRITE->autoflush(1); 
WRITE2->autoflush(1); 
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
	$ret[0]=~s/\./,/g;
	my ($val, $uncert)=split(/\+\/\-/, $ret[0]); 
	if ($uncert) {
		# This part ist 
		my $cnt=$uncert; 
		$cnt=~s/^(0|,)+//g;
		$cnt=length($cnt);
		if ( $cnt < 2 ) {
			# we need to add one significant zero
			# because it is a standard! 
			$uncert=$uncert."0";
		}
		while (length($val)< length($uncert)) {
			$val=$val."0";
		} 
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
		print WRITE2; 
		s/^%calc\ *//g;
		chomp;
		my $n="\n";
		if (/\r$/) { chop; $n="\r\n"; print "Dos Format detected\n";}
		s/%.+?$//g; # strip comments 
		#$_=$_."\n";
		# calc that 
		foreach my $result (calculate($_)) {
			print WRITE "%res ".$result.$n; 
			print WRITE2 "%res ".$result.$n; 
		}
	} elsif (/^%res/) {
		# do nothing with result lines 
	} else { 
		print WRITE; 
		s/\@((\w|\d)+)\@/insert_pyvar($1)/gex; 
		print WRITE2; 
	}
}

close READ; 
close WRITE; 
close WRITE2; 

unlink($texfile) or die "TMP"; 
if (!$pdflatex) {
	link(".$texfile.tmp", $texfile) or die "TMP"; 
	unlink(".$texfile.tmp") or die "TMP"; 
	unlink(".$texfile.tmp2") or die "TMP"; 
} else {
	link(".$texfile.tmp2", $texfile) or die "TMP"; 

	system("$pdflatex $texfile") or print "calling pdflatex failed\n"; 
	system("$pdflatex $texfile") or print "calling pdflatex failed\n"; 
	
	if ( ! $leavetexfile) {
		unlink($texfile) or die "TMP"; 
		link(".$texfile.tmp", $texfile) or die "TMP"; 
	}
	unlink(".$texfile.tmp") or die "TMP"; 
	unlink(".$texfile.tmp2") or die "TMP"; 
}

