import torch


def accuracy(output, target):
    with torch.no_grad():
        pred = torch.argmax(output, dim=1)
        assert pred.shape[0] == len(target)
        correct = 0
        correct += torch.sum(pred == target).item()
    return correct / len(target)


def top_k_acc(output, target, k=3):
    with torch.no_grad():
        pred = torch.topk(output, k, dim=1)[1]
        assert pred.shape[0] == len(target)
        correct = 0
        for i in range(k):
            correct += torch.sum(pred[:, i] == target).item()
    return correct / len(target)


def tsne_features(image_features, y_true, subset):

    tsne = TSNE(n_components=2)
    X_tsne = tsne.fit_transform(image_features, y_true)

    fig, ax = plt.subplots(figsize=(10, 10), dpi=200)
    colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'pink']
    for i, c in enumerate(set(y_true)):
        mask = (y_true == c)
        ax.scatter(X_tsne[mask, 0], X_tsne[mask, 1], label=test_dataset.classes[i], c=colors[i], alpha=0.7)
    ax.legend()
    ax.set_title("t-SNE of the " + subset + " images features\n (ResNet50 output of last convolutional layer)")
    fig.savefig("Results/Task_a/tsne_" + subset + "_features.png")

def plot_retrieval(test_images, train_images, y_true_test, y_true_train, neigh_ind, neigh_dist, p="BEST", num_queries=6, num_retrievals=6):

    if p=="BEST":
        ind = np.argsort(np.sum(neigh_dist[:, 0:5], axis=1), axis=0)
        title = "Test query images that obtained retrieved images \nwith the lowest distance among the dataset\n"
    elif p=="WORST":
        ind = np.argsort(-np.sum(neigh_dist[:, 0:5], axis=1), axis=0)
        title = "Test query images that obtained retrieved images \nwith the highest distance among the dataset\n"
    else:
        title = "First test query images and their retrieved train images\n"

    if p=="BEST" or p=="WORST":
        test_images = test_images[ind]
        y_true_test = y_true_test[ind]
        neigh_ind = neigh_ind[ind]
        neigh_dist = neigh_dist[ind]

    fig, ax = plt.subplots(num_queries, num_retrievals, figsize=(10, 10), dpi=200)
    fig.suptitle(title)
    for i in range(0, num_queries):
        ax[i][0].imshow(np.moveaxis(test_images[i], 0, -1))
        ax[i][0].set_title("Test set \nquery image \nClass: " + str(y_true_test[i]))
        ax[i][0].set_xticks([])
        ax[i][0].set_yticks([])
        for j in range(1, num_retrievals):
            ax[i][j].imshow(np.moveaxis(train_images[neigh_ind[i][j]], 0, -1))
            ax[i][j].set_title("Retrieved image\n Distance: " + str(round(neigh_dist[i][j], 2)) + "\nClass: " + str(y_true_train[neigh_ind[i][j]]))
            ax[i][j].set_xticks([])
            ax[i][j].set_yticks([])
    fig.tight_layout()
    plt.savefig("Results/Task_a/ImageRetrievalQualitativeResults_" + p + ".png")
    plt.close()
