1Problem Statement & Motivation
1.1 Problem Statement
In modern blockchain ecosystems, users usually interact with the network through wallet such as browser wallets and mobile wallets, which rely on Remote Procedure Call (RPC) providers to query blockchain state and submit transactions. Though the transparency is one of the design features of blockchain, privacy risks introduced at the wallet–RPC communication layer tend to be ignored in practice.
RPC communication may leak not only on-chain information, but also sensitive metadata, including: 
•	Query patterns and call frequency
•	Temporal behavior signatures
•	Address usage correlations
•	Network-level indicators that enable location inference
An honest-but-curious RPC provider can still leverage this metadata to link user addresses, infer behavior patterns, or reduce user anonymity without modifying blockchain state or breaking cryptographic protections. So the goal of this project is to measure and quantify such privacy leakage systematically using real wallet-RPC communication data instead of relying merely on theoretical analysis.
1.2 Motivation
The motivation of this project includes:
•	Practical relevance: Wallet–RPC communication is a core infrastructure component used by millions of users daily.
•	Measurement gap: Existing discussions of RPC privacy risks lack standardized, empirical quantification.
•	Actionability: Measurement-based findings can directly inform wallet developers, RPC providers, and users.
By focusing on the communication behaviors that can be observed by attackers, this project contributes to privacy-enhancing technologies through empirical evidence rather than speculative threat discussions.
2. Scope & Boundaries
2.1 In-Scope Components
This project focuses on:
•	JSON-RPC request metadata (method types, timing, frequency)
•	Session- and address-level behavior patterns
•	Wallet–RPC interaction traces under realistic usage scenarios
•	Quantitative privacy metrics derived from captured traffic
2.2 Out-Scope Components
To maintain a realistic and bounded threat model, the following content are excluded:
•	Compromise of wallet software or private keys
•	Breaking TLS or cryptographic primitives
•	Blockchain consensus manipulation
•	Legal or regulatory compliance analysis
3. Threat Model
3.1 Adversary Definition
We define an honest-but-curious RPC provider as the adversary. The RPC provider correctly executes all requests and provides valid responses, but passively observes and records RPC communication metadata for analysis purposes.
3.2 Adversary Capabilities
Under this threat model, the adversary is able to observe the following information:
•	JSON-RPC method names such as eth_getBalance and eth_call
•	Request timing, frequency, and ordering
•	Session-level and address-level request patterns
•	Network-level identifiers associated with requests (e.g., IP address or session identifier)
The adversary is assumed to have long-term storage and offline analysis capabilities over the collected metadata.
3.3 Adversary Limitations:
The adversary cannot:
•	Modify blockchain state or transaction execution results
•	Break cryptographic primitives or TLS encryption
•	Access wallet-internal state, private keys, or user devices
4. Core Capabilities for Privacy Measurement
To support empirical privacy analysis under the defined threat model, the proposed system provides the following core capabilities:
•	Capture and log RPC request metadata observable by an RPC provider, including method names, timing, and frequency
•	Organize captured requests into session-level and address-level interaction traces
•	Compute quantitative privacy-related metrics that reflect user linkability and behavioral distinguishability
•	Compare privacy leakage across controlled usage scenarios
5. Initial Specification
This project follows a specification-driven development approach, where privacy requirements are defined prior to implementation and validated through empirical measurement.
5.1 Assumptions
The following assumptions are made throughout this project:
•	RPC providers have full visibility into RPC request metadata
•	Users do not actively attempt to obfuscate their RPC traffic
•	Blockchain execution and consensus mechanisms are trusted and operate correctly
5.2 Security and Privacy Invariants
The system should satisfy the following security and privacy invariants:
•	Independent users should not be trivially linkable using RPC metadata alone
•	Using multiple blockchain addresses should reduce, rather than preserve, user linkability
•	RPC metadata should not enable high-confidence user identification under ideal privacy assumptions
6. Validation and Experiment Plan
This project adopts a measurement-driven validation approach, where each experiment directly corresponds to the defined threat model.
Experiment1: Address Linkability Measurement
Goal: To measure whether different users can be distinguished by RPC usage behavior.
The relationship with threat model: RPC providers observe request patterns, timing and ordering.
Experiment 2: Behavioral Fingerprinting
Goal: To evaluate whether different users can be distinguished based on RPC usage behavior.
The relationship with threat model: Temporal and frequency-based metadata may reveal behavioral signatures.
Experiment 3: Scenario-Based Comparison (Optional Extension)
Goal: To compare privacy leakage across different usage scenarios, such as single versus multiple addresses or sessions.
The relationship with threat model: Variations in observable metadata may affect linkability and entropy.
