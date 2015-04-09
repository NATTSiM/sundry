//------------------------------------------------------------------------------
/*
    Copyright (c) 2015 Ripple Labs Inc.

    Permission to use, copy, modify, and distribute this software for any
    purpose with or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.

    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
*/
//------------------------------------------------------------------------------

// build with: cc -Wall -O3 rsign.c -o rsign -lrippled

#include <ripple.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <arpa/inet.h>
#include <string.h>
#include <stddef.h>
#ifndef _BSD_SOURCE
#define _BSD_SOURCE
#endif
#include <endian.h>

void readStdin (void* buf, size_t count);

int main (int argc, char** argv)
{
    int flags;

    flags = fcntl (STDIN_FILENO, F_GETFL, 0);
    fcntl (STDIN_FILENO, F_SETFL, flags & (~O_NONBLOCK));
    flags = fcntl (STDOUT_FILENO, F_GETFL, 0);
    fcntl (STDOUT_FILENO, F_SETFL, flags & (~O_NONBLOCK));

    while (1)
    {
        uint32_t bufSize, docSize;
        char* buf;

        readStdin (&bufSize, sizeof (bufSize));
        docSize = be32toh (bufSize);

        if (docSize)
        {
            char* signedBuf;
            size_t signedLen;

            buf = malloc (docSize);
            if (buf == NULL)
            {
                fprintf (stderr, "Can't allocate %u bytes.\n", docSize);
                exit (1);
            }
            readStdin (buf, docSize);
            ripple_transaction_sign (buf, docSize, &signedBuf, &signedLen);
            if (signedLen)
            {
                char *outBuf;
                uint32_t signedBufSize, s;
                ssize_t w;
                uint32_t pos = 0;

                signedBufSize = htobe32 ((uint32_t)signedLen);
                s = sizeof (signedBufSize) + signedLen;
                outBuf = malloc (s);
                if (outBuf == NULL)
                {
                    fprintf (stderr, "Can't allocate %u bytes.\n", s);
                    exit (2);
                }
                memcpy (outBuf, &signedBufSize, sizeof (signedBufSize));
                memcpy (outBuf + sizeof (signedBufSize), signedBuf, signedLen);

                do
                {
                    w = write (STDOUT_FILENO, (char*)buf + pos, s - pos);
                    if (w > -1)
                    {
                        pos += w;
                    }
                    else
                    {
                        perror (NULL);
                        exit (3);
                    }
                } while (pos < s);

                ripple_free (signedBuf);
                free (outBuf);
            }

            free (buf);
        }
    }

    return 0;
}

void readStdin (void* buf, size_t count)
{
    size_t pos = 0;
    ssize_t r;

    do
    {
        r = read (STDIN_FILENO, (char*)buf + pos, count - pos);
        switch (r)
        {
            case -1:
                perror (NULL);
                exit (4);
            case 0:
                exit (5);
            default:
                pos += r;
        }
    } while (pos < count);

    return;
}
