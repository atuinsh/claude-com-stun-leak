Hi Anthropic,

My name is Marko, and I'm one of the engineers working at https://atuin.sh. This email is to notify
you of a security vulnerability I believe to have identified with the
[Artifacts](https://claude.ai/artifact) system enabling a forged artifact to leak IP addresses of
all users visiting the artifact.

### Attack description

1. The attacker hosts a [STUN](https://en.wikipedia.org/wiki/STUN) server on a machine they
   control.
2. The attacker sets up a malicious Claude.ai artifact which embeds an `iframe` such that the
   `iframe` performs an
   [`RTCPeerConnection`](https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection) to the
   attacker's server within the iframe.
3. The attacker shares this artifact to the victim.
4. When the victim opens the shared artifact, their IP is sent to the attacker's server, leaking
   their IP.

WebRTC is known by the technical community to be wildly insecure and IP-leaky, so I suspect
some advanced users will have WebRTC blockers, however, I imagine that the vast majority of your
users do not have blockers.

### Existing Mitigation

It appears that you have some existing mitigation in-place for IP leaks of this class. It seems
that `RTCPeerConnection` is undefined inside the Javascript context running inside the context. I
am guessing that you have monkey-patched it out.

Unfortunately, this does nothing to guard another Javascript context, which is exactly why the
attacker needs to inject an `iframe` within the artifact, creating a new context.

Consequently, since it appears you have some mitigations in place, I suspect that you aim to
protect your users against these kinds of attacks.

### Proof

This email includes a minimal `.tar.gz` reproducing the attack. We also have a private github repo
we are happy to share with you, with the exact same information, if that is more convenient. The
following files are relevant:

- `stun_server.py` includes a minimal vibe-coded STUN server, which the attacker hosts on their
  server.
- `claude-ai-artifacts-export.html` includes the artifact (mentioned last) exported via the Export
  UI in Claude Artifacts.
- **Open responsibly** `https://claude.ai/artifact/4HWQGMvp7Ezr2JihVyYZau` is the sharable
  artifact which performs the STUN-based IP leak. It has a text-box which enables you to plug in
  your own IP.

Additional files, which are helpful to reproduce the issue:

- `probe.html` includes a small web-page which leaks the victim's IP address. 
- `Makefile` is a mostly self-contained makefile for deploying the `stun_server.py` on the
  attacker's server.

To tweak this example you should tweak the following values:

| Value | Description |
|-------|-------------|
| `probe.html:stunLink` | The IP address of the STUN server. |
| `Makefile:SERVER` | The IP address of the STUN server. |

The values are pre-programmed with a Latitude VPS we have control over. We are happy to provide you
with SSH access to this box as we have provisioned it for this purpose alone.

### Suggestion

Two solutions appear to work here:

1. Parse the artifact and ensure there are no `iframe`s within its source.
2. Run a safer, bundled, controlled javascript execution context based on
   [QuickJS](https://bellard.org/quickjs/) which, at the engine level, removes `RTCPeerConnection`.

I surmise that the first solution is difficult, bug-prone, and potentially still insecure, as a
malicious attacker could simply "un-patch" `RTCPeerConnection`, if lower-level, undocumented
browser APIs exist at this point, or at any point in the future.

The second solution is more involved, however, appears to be total. At Atuin, we are currently
exploring the latter option for our own secure application. We would be more than happy to share
our React components with you, as OSS under MIT if you wish to use them.

We have not disclosed this minor-medium vulnerability and eagerly await your response. If we fail
to hear back from you within 90 days, we will disclose the concern publicly. We're very happy to
share our work in creating safe(r) `iframe` environments with you, as we progress on our end.

- Marko Vejnovic @ Atuin.sh

PS. If I fail to respond to any of your emails in a timely manner, please feel free to reach out to
anyone CCed in this email or `engineering@atuin.sh`.
