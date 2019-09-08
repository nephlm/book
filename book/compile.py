import subprocess


def compile_to_epub(src_md, dst_epub):
    """
    src_md and dst_epub are all paths.

    Runs an appropriate pandoc command to create and epub file at the location specified by 
    dst_epub.

    pandoc -o dst_epub metadata.yaml src_md -t epub3
    --toc --toc-depth=2 --epub-stylesheet=... --epub-chapter-level=2 --number-sections
    --smart
    --css
    """
    print(f'compiling {src_md} to {dst_epub}')
    cmd = [
        'pandoc',
        '-o',
        dst_epub,
        src_md,
        '--toc',
        '--toc-depth',
        '2',
        '--epub-chapter-level',
        '2',
        '--number-sections',
        '--smart',
        '--verbose',
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    print(stdout)
    print(stderr)
