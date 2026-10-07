# src/ — DSP-Kern und LV2-Wrapper

`dsp/GreenStripe.hpp` (Signalfluss), `dsp/Transformer.hpp` +
`dsp/TransformerModels.hpp` (Transformator-Laufzeit), `dsp/ModelConstants.hpp`
(generierte Konstanten) und `lv2_plugin.cpp` (C-ABI-Wrapper, 2 Deskriptoren
Mono/Stereo). C++11, kein Fast-Math, `-ffp-contract=off`.
