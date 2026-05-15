add_cus_dep('bbl', 'generated_bbl', 0, 'copy_bbl_for_main_job');

$max_repeat = 8;

sub copy_bbl_for_main_job {
    my ($base) = @_;
    my $source = "$base.bbl";
    my $dest = "$base.generated_bbl";

    return 0 unless -e $source;

    open my $in, '<:raw', $source or return 1;
    open my $out, '>:raw', $dest or return 1;

    while (read($in, my $buffer, 8192)) {
        print {$out} $buffer or return 1;
    }

    close $in or return 1;
    close $out or return 1;
    return 0;
}
