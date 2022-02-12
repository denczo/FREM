from pylatexenc.latex2text import LatexNodes2Text


class InfoText:
    part1 = "\n\n[b]Welcome to FREM [/b] \n\n[b]FREM[/b] is a tool to show how frequency modulation" \
            " mathematically works which is also widely used in synthesizers (e.g. vibrato " \
            "effect). For frequency modulation you will need at least two waveforms. One acts " \
            "as [b]Modulating Wave[/b], the other one as [b]Carrier Wave[/b]. This tool provides " \
            "[b]three[/b] waveforms, which means two modulating waves can be applied on one " \
            "carrier wave.\n"

    part2 = "\n[b]How to use FREM?[/b]\n\nFor each waveform it can be switched " \
            "between four types: [b]Sine[/b], [b]Sawtooth[/b], [b]Triangle[/b] and [b]Square[/b]." \
            " Each type has a different formula which will be shown and also can be visualized " \
            "(shown in fig 1.1). For a closer look you can also zoom in.\n"

    part3 = "\n\n[b]visible Graph: [/b] visualises the graph of the current selected waveform. " \
            "The graph represents [color=FF0000]one second[/color]. The audio however is rendered" \
            " in realtime as long as it's played. The played audio is not a loop!" \
            "\n\n[b]Modulation Index: [/b] describes the factor, how much the modulation will be " \
            "applied on the carrier wave (fig 1.2). \n\n[b]calculate F(x): [/b] integrates the " \
            "formula of the selected waveform and enables the [b]Modulation Index[/b] (fig 1.2).\n"

    part4 = "\n\n[b]Carrier Wave: " \
            "[/b] each waveform can be the carrier wave on which the modulating wave will be " \
            "applied. E.g. [color=08F7FE]Modulating Wave[/color] [color=FE53BB]Carrier " \
            "Wave[/color] or [color=FE53BB]Modulating Wave[/color] [color=00ff41]Carrier " \
            "Wave[/color] \n\n[b]Modulating Wave: [/b] each waveform can be also the modulating " \
            "wave except for the [color=00ff41]last one[/color]. " \
            "To apply the modulating wave onto the carrier wave, the discrete integration of the " \
            "waveform needs to be calculated ([b] calculate F(x)[/b] ).\n\n[b]PLAY:[/b] plays " \
            "the carrier wave with it's applied modulation.\n"

    part5 = "\n\n\n[b]Quick overview behind the maths[/b]" \
            "\n\nThe maths behind frequency modulation works the same for all waveforms. Let's " \
            "take as example the sine wave. As already mentioned we need a carrier wave and " \
            "a modulation wave to do frequency modulation. Let's start with the formula " \
            "for the [b]carrier wave[/b]:" \
            "\n\n[b][size=20sp]" + LatexNodes2Text().latex_to_text(r'$a \sin(2\pi f x + m)$') + "[/size][/b]" \
            "\n\n[i]a: amplitude (signal strength)\nf: frequency\nx: individual sample on x-axis" \
            "\nm: modulating wave e.g. " \
            "[b]" + LatexNodes2Text().latex_to_text(r'$a \sin(2\pi f x)$') + ", 0 if not set[/b][/i]" \
            "\n\nTo render a waveform with a given frequency the amount of samples needs to be " \
            "at least 2 times the frequency. " \
            "If you would like to render a waveform with 20khz (20.000hz) which is the highest " \
            "frequency most people are able to hear, you would at least require 40.000 samples." \
            "Therefore in the music industry often a sampling-rate of 44.1khz is used which " \
            "basically tells us that the audio is rendered with 44.100 samples per second." \
            "\n\n\nThe modulating wave is simply another carrier wave. Let's have a look how " \
            "this [b]modulating wave[/b] can be applied on the carrier wave:\n\n" \
            "[size=20sp]" + LatexNodes2Text().latex_to_text(r'$a[sub]c[/sub] \sin(2\pi f[sub]c[/sub] x[sub]c[/sub] '
            r'+ [b]\beta a[sub]m[/sub] \int\ sin(2\pi f[sub]m[/sub] x[sub]m[/sub])dx[/b])$') + "[/size]" \
            "\n\n" + LatexNodes2Text().latex_to_text(
            r'$[i]\beta$') + ": modulation index (" + LatexNodes2Text().latex_to_text(
            r'$f[sub]\Delta[/sub]/f[sub]m[/sub]$') + ")" \
            "\na[sub]m[/sub]: amplitude modulation wave\nf[sub]m[/sub]: frequency modulation wave" \
            "\nx[sub]m[/sub]: individual sample of modulation wave on x-axis\n\n\n" \
            "To calculate the integral you first will need to calculate all the samples for " \
            "the modulation wave. After that you apply the [b]running sum[/b] on each of " \
            "those samples and that's it:\n\n[b][size=20sp]x[sub]n[/sub] = x[sub]n[/sub] - x[sub]" \
            "n-1[/sub][/size][/b]\n\nx[sub]n[/sub]: individual sample\nfor n = 0:x[sub]n-1[/sub] = 0" \
            "\n\nIn the last step you will need to [b]normalize[/b] the samples of your modulating wave." \
            "After that you can simply add each sample of the modulating wave to each sample of" \
            "the carrier wave (just like in the formula). \n\n[size=20sp][b]x[sub]n[/sub] = x[sub]n[/sub]" \
            " - min(x) / max(x) - min(x)[/b][/size]\n\nx[sub]n[/sub]: individual sample\nx: all samples"
