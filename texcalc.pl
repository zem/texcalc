#!/usr/bin/perl

use IPC::Open3;
use IO::Handle;
use IO::Select; 

my $leavetexfile; 
my $pdflatex; 
my $texfile; 
my $texcmd="pdflatex";
while (my $arg=shift(@ARGV)) {
	if ($arg eq "-c") {
		# -compile
		$pdflatex=$texcmd; 
	} elsif (($arg eq "-?")or($arg eq "-h")) {
		print "
	usage: $0  [-tex latexcommand] [-C -y] [-c] [-?|-h] filename
		-tex	configures the latex command to produce pdf files default ist pdflatex
		-C	-y	exchanges the \@VARIABLE\@ Tags in the .tex file with the calculated values
		-c		calculates the the file and produces tex
		-?
		-h 	prints this help
				
"; 
		exit ; 
	} elsif ($arg eq "-tex") {
		$texcmd=shift(@ARGV); 
		# in the case anyone already issued -c or -C 
		if ( $pdflatex ) { $pdflatex=$texcmd; }
	} elsif ($arg eq "-C") {
		if (shift(@ARGV) eq "-y") {
			# -compile
			$pdflatex=$texcmd; 
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

sub length_after_delim  {
	my ($val, $dezimal)=split(/,/, shift);
 	return length ($dezimal)	
}

sub insert_pyvar {
	my ($var, $digits)=split(/\,/, shift);
	print "Insertin Variable $var\n"; 
	if ( ! $digits ) { $digits=2; }
	my @ret=calculate("uround($var, $digits)"); 
	$ret[0]=~s/^\s+//g; 
	$ret[0]=~s/\s+$//g; 
	$ret[0]=~s/\./,/g;
	my ($val, $uncert)=split(/\+\/\-/, $ret[0]); 
	$val=~s/,0$//g;
	$uncert=~s/,0$//g;
	if ($uncert) {
		# This part ist 
		if ( $uncert !~ /,/ ) { $uncert=$uncert."," }
		my $cnt=$uncert; 
		$cnt=~s/^(0|,)+//g;
		my $cnt_num=length($cnt);
		while ( $cnt_num < $digits ) {
			# we need to add one significant zero
			# because it is a standard! 
			$uncert=$uncert."0";
			$cnt=$cnt."0"; $cnt_num=length($cnt);
		}
		if ((length_after_delim($val)< length_after_delim($uncert)) and ( $val !~ /,/ )) { $val=$val."," }
		while (length_after_delim($val)< length_after_delim($uncert)) {
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
	if ((/^%calc/)or(/^%c\ /)or(/^%C\ /)) {
		print WRITE; 
		print WRITE2; 
		my $with_result;
		if (/^%C\ /){ $with_result=1; }
		s/^%calc\ *//g;
		s/^%c\ +//g;
		s/^%C\ +//g;
		chomp;
		my $n="\n";
		if (/\r$/) { chop; $n="\r\n"; print "Dos Format detected\n";}
		s/%.+?$//g; # strip comments 
		s/\(((\d|\.)+)\|((\d|\.)+)\)/"f((".$1.",".$3."))"/gex; # (23.2|0.01) 
		#$_=$_."\n";
		# calc that 
		foreach my $result (calculate($_)) {
			print WRITE "%r ".$result.$n; 
			print WRITE2 "%r ".$result.$n; 
		}
		if ($with_result) {
			#we will do the last thing again but trying to fetch the Variable 
			s/=.*$//g;
			foreach my $result (calculate($_)) {
				print WRITE "%r ".$result.$n; 
				print WRITE2 "%r ".$result.$n; 
			}
		}
	} elsif ((/^%res/)or(/^%r\ /)) {
		# do nothing with result lines 
	} else { 
		print WRITE; 
		s/\@((\w|\d|\,)+)\@/insert_pyvar($1)/gex; 
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

